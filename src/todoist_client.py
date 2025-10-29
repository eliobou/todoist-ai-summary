"""
Client pour interagir avec l'API Todoist
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class TodoistClient:
    """Client pour l'API Todoist avec retry automatique"""
    
    BASE_URL = "https://api.todoist.com/sync/v9"
    REST_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self):
        self.api_token = os.getenv('TODOIST_API_TOKEN')
        if not self.api_token:
            raise ValueError("TODOIST_API_TOKEN manquant dans .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Configuration des préfixes de projets (facilement modifiable)
        self.work_prefix = os.getenv('WORK_PREFIX', 'ECL')
        self.personal_prefix = os.getenv('PERSONAL_PREFIX', 'Perso')
        self.tinker_prefix = os.getenv('TINKER_PREFIX', 'Tinker')
        
        # Session avec retry automatique
        self.session = self._create_session()
        
        # Cache des projets
        self._projects_cache = None
    
    def _create_session(self) -> requests.Session:
        """Crée une session avec retry automatique"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Récupère la liste des projets"""
        if self._projects_cache is not None:
            return self._projects_cache
        
        logger.info("Récupération de la liste des projets...")
        response = self.session.get(
            f"{self.REST_URL}/projects",
            headers=self.headers
        )
        response.raise_for_status()
        
        self._projects_cache = response.json()
        logger.info(f"  {len(self._projects_cache)} projets trouvés")
        return self._projects_cache
    
    def get_sections(self, project_id: str) -> List[Dict[str, Any]]:
        """Récupère les sections d'un projet"""
        response = self.session.get(
            f"{self.REST_URL}/sections",
            headers=self.headers,
            params={"project_id": project_id}
        )
        response.raise_for_status()
        return response.json()
    
    def get_completed_tasks(
        self, 
        start_date: datetime.date, 
        end_date: datetime.date
    ) -> List[Dict[str, Any]]:
        """
        Récupère les tâches complétées entre deux dates
        
        Args:
            start_date: Date de début (incluse)
            end_date: Date de fin (incluse)
        
        Returns:
            Liste des tâches complétées avec leur projet et section
        """
        logger.info(f"Récupération des tâches du {start_date} au {end_date}...")
        
        # Récupération de tous les projets
        projects = self.get_projects()
        projects_map = {p['id']: p for p in projects}
        
        # Récupération des sections pour chaque projet
        sections_map = {}
        for project in projects:
            sections = self.get_sections(project['id'])
            for section in sections:
                sections_map[section['id']] = section
        
        # Récupération des tâches complétées via l'API Sync
        # On récupère depuis 8 jours pour être sûr de tout avoir
        since = (start_date - timedelta(days=1)).isoformat()
        
        response = self.session.get(
            f"{self.BASE_URL}/completed/get_all",
            headers=self.headers,
            params={"since": since}
        )
        response.raise_for_status()
        data = response.json()
        
        # Filtrage des tâches dans la période voulue
        completed_tasks = []
        for item in data.get('items', []):
            completed_at_str = item.get('completed_at')
            if not completed_at_str:
                continue
            
            # Parse de la date de complétion
            completed_at = datetime.fromisoformat(
                completed_at_str.replace('Z', '+00:00')
            ).date()
            
            # Vérification de la période
            if start_date <= completed_at <= end_date:
                task_data = {
                    'id': item.get('id'),
                    'content': item.get('content'),
                    'completed_at': completed_at_str,
                    'project_id': item.get('project_id'),
                    'section_id': item.get('section_id'),
                    'project_name': None,
                    'section_name': None
                }
                
                # Ajout du nom du projet
                if item.get('project_id') in projects_map:
                    task_data['project_name'] = projects_map[item['project_id']]['name']
                
                # Ajout du nom de la section
                if item.get('section_id') and item['section_id'] in sections_map:
                    task_data['section_name'] = sections_map[item['section_id']]['name']
                
                completed_tasks.append(task_data)
        
        logger.info(f"  {len(completed_tasks)} tâches dans la période")
        return completed_tasks
    
    def _parse_project_name(self, project_name: str) -> tuple[str, str]:
        """
        Parse le nom d'un projet pour extraire le préfixe et le sous-projet
        
        Args:
            project_name: Nom complet du projet (ex: "ECL/Vision")
        
        Returns:
            Tuple (prefix, subproject) ex: ("ECL", "Vision")
            Si pas de "/", retourne (project_name, None)
        """
        if '/' in project_name:
            parts = project_name.split('/', 1)
            return parts[0], parts[1]
        return project_name, None
    
    def organize_tasks_by_category(
        self, 
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Organise les tâches par catégorie et sous-projet
        
        Returns:
            Dict avec structure:
            {
                'ECL': {
                    'Vision': [tasks...],
                    'Scripting backup purge': [tasks...]
                },
                'Perso': {
                    None: [tasks...]  # Si pas de sous-projet
                },
                'Tinker': {
                    'Horloge connectée': [tasks...],
                    'Bot Discord': [tasks...]
                }
            }
        """
        organized = {}
        
        for task in tasks:
            project_name = task.get('project_name', '')
            if not project_name:
                continue
            
            # Parse du nom du projet
            prefix, subproject = self._parse_project_name(project_name)
            
            # Vérification que c'est un préfixe configuré
            if prefix not in [self.work_prefix, self.personal_prefix, self.tinker_prefix]:
                # Projet qui ne correspond à aucun préfixe configuré
                continue
            
            # Initialisation de la structure si nécessaire
            if prefix not in organized:
                organized[prefix] = {}
            
            # Clé pour le sous-projet (None si pas de sous-projet)
            subproject_key = subproject if subproject else None
            
            if subproject_key not in organized[prefix]:
                organized[prefix][subproject_key] = []
            
            organized[prefix][subproject_key].append(task)
        
        # Log de l'organisation
        for prefix, subprojects in organized.items():
            total = sum(len(tasks) for tasks in subprojects.values())
            logger.info(f"  - {prefix}: {total} tâches")
            for subproject, tasks in subprojects.items():
                if subproject:
                    logger.info(f"    └─ {subproject}: {len(tasks)} tâches")
        
        return organized
