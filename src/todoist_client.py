"""
Client for interacting with Todoist API
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
    """Client for Todoist API with automatic retry"""
    
    BASE_URL = "https://api.todoist.com/sync/v9"
    REST_URL = "https://api.todoist.com/rest/v2"
    
    def __init__(self):
        self.api_token = os.getenv('TODOIST_API_TOKEN')
        if not self.api_token:
            raise ValueError("TODOIST_API_TOKEN missing in .env")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        
        # Project prefix configuration (easily modifiable)
        self.work_prefix = os.getenv('WORK_PREFIX', None)
        self.personal_prefix = os.getenv('PERSONAL_PREFIX', None)
        self.tinker_prefix = os.getenv('TINKER_PREFIX', None)

        if self.work_prefix is None or self.personal_prefix is None or self.tinker_prefix is None:
            raise ValueError("Projects prefix not set")
        
        # Session with automatic retry
        self.session = self._create_session()
        
        # Projects cache
        self._projects_cache = None
    
    def _create_session(self) -> requests.Session:
        """Create a session with automatic retry"""
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
        """Fetch list of projects"""
        if self._projects_cache is not None:
            return self._projects_cache
        
        logger.info("Fetching project list...")
        response = self.session.get(
            f"{self.REST_URL}/projects",
            headers=self.headers
        )
        response.raise_for_status()
        
        self._projects_cache = response.json()
        logger.info(f"  {len(self._projects_cache)} projects found")
        return self._projects_cache
    
    def get_sections(self, project_id: str) -> List[Dict[str, Any]]:
        """Fetch sections of a project"""
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
        Fetch completed tasks between two dates
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        
        Returns:
            List of completed tasks with their project and section
        """
        logger.info(f"Fetching tasks from {start_date} to {end_date}...")
        
        # Fetch all projects
        projects = self.get_projects()
        projects_map = {p['id']: p for p in projects}
        
        # Fetch sections for each project
        sections_map = {}
        for project in projects:
            sections = self.get_sections(project['id'])
            for section in sections:
                sections_map[section['id']] = section
        
        # Fetch completed tasks via Sync API
        # Fetch from 8 days ago to ensure we get everything
        since = (start_date - timedelta(days=1)).isoformat()
        
        response = self.session.get(
            f"{self.BASE_URL}/completed/get_all",
            headers=self.headers,
            params={"since": since}
        )
        response.raise_for_status()
        data = response.json()
        
        # Filter tasks within the desired period
        completed_tasks = []
        for item in data.get('items', []):
            completed_at_str = item.get('completed_at')
            if not completed_at_str:
                continue
            
            # Parse completion date
            completed_at = datetime.fromisoformat(
                completed_at_str.replace('Z', '+00:00')
            ).date()
            
            # Check period
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
                
                # Add project name
                if item.get('project_id') in projects_map:
                    task_data['project_name'] = projects_map[item['project_id']]['name']
                
                # Add section name
                if item.get('section_id') and item['section_id'] in sections_map:
                    task_data['section_name'] = sections_map[item['section_id']]['name']
                
                completed_tasks.append(task_data)
        
        logger.info(f"  {len(completed_tasks)} tasks in period")
        return completed_tasks
    
    def _parse_project_name(self, project_name: str) -> tuple[str, str]:
        """
        Parse project name to extract prefix and subproject
        
        Args:
            project_name: Full project name (e.g., "ECL/Vision")
        
        Returns:
            Tuple (prefix, subproject) e.g., ("ECL", "Vision")
            If no "/", returns (project_name, None)
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
        Organize tasks by category and subproject/section
        
        Returns:
            Dict with structure:
            {
                'ECL': {
                    'Vision': [tasks...],
                    'Scripting backup purge': [tasks...]
                },
                'Perso': {
                    'Maison': [tasks...],  # Section used as subproject
                    'Admin': [tasks...]
                },
                'Tinker': {
                    'Connected Clock': [tasks...],
                    'Discord Bot': [tasks...]
                }
            }
        """
        organized = {}
        
        for task in tasks:
            project_name = task.get('project_name', '')
            if not project_name:
                continue
            
            # Parse project name
            prefix, subproject = self._parse_project_name(project_name)
            
            # Check if it's a configured prefix
            if prefix not in [self.work_prefix, self.personal_prefix, self.tinker_prefix]:
                # Project doesn't match any configured prefix
                continue
            
            # Initialize structure if needed
            if prefix not in organized:
                organized[prefix] = {}
            
            # Determine the key for grouping:
            # 1. If there's a subproject (after /), use it
            # 2. Otherwise, use the section name
            # 3. If neither, use None
            if subproject:
                grouping_key = subproject
            elif task.get('section_name'):
                grouping_key = task['section_name']
            else:
                grouping_key = None
            
            if grouping_key not in organized[prefix]:
                organized[prefix][grouping_key] = []
            
            organized[prefix][grouping_key].append(task)
        
        # Log organization
        for prefix, subprojects in organized.items():
            total = sum(len(tasks) for tasks in subprojects.values())
            logger.info(f"  - {prefix}: {total} tasks")
            for subproject, tasks in subprojects.items():
                if subproject:
                    logger.info(f"    └─ {subproject}: {len(tasks)} tasks")
        
        return organized