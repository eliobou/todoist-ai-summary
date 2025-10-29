"""
Gestionnaire de stockage local pour les résumés
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class StorageManager:
    """Gère la sauvegarde et le chargement des résumés"""
    
    def __init__(self):
        self.data_dir = Path("data/summaries")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Répertoire de stockage : {self.data_dir.absolute()}")
    
    def save_summary(
        self,
        summary: str,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date
    ) -> None:
        """
        Sauvegarde le résumé au format JSON et Markdown
        
        Args:
            summary: Le résumé généré
            organized_tasks: Les tâches organisées par catégorie et sous-projet
            week_start: Date de début de semaine
            week_end: Date de fin de semaine
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        week_str = f"{week_start.strftime('%Y%m%d')}-{week_end.strftime('%Y%m%d')}"
        
        # Calcul des statistiques
        stats = self._calculate_stats(organized_tasks)
        
        # Préparation des données
        data = {
            'generated_at': datetime.now().isoformat(),
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'summary': summary,
            'tasks': organized_tasks,
            'stats': stats
        }
        
        # Sauvegarde JSON
        json_file = self.data_dir / f"summary_{week_str}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"  Sauvegardé : {json_file.name}")
        
        # Sauvegarde Markdown (plus lisible)
        md_file = self.data_dir / f"summary_{week_str}_{timestamp}.md"
        markdown_content = self._generate_markdown(
            summary=summary,
            organized_tasks=organized_tasks,
            week_start=week_start,
            week_end=week_end,
            stats=stats
        )
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        logger.info(f"  Sauvegardé : {md_file.name}")
    
    def _calculate_stats(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> Dict[str, Any]:
        """Calcule les statistiques des tâches"""
        stats = {
            'total_tasks': 0,
            'by_category': {},
            'by_subproject': {}
        }
        
        for category, subprojects in organized_tasks.items():
            category_total = 0
            stats['by_subproject'][category] = {}
            
            for subproject_name, tasks in subprojects.items():
                task_count = len(tasks)
                category_total += task_count
                
                if subproject_name:
                    stats['by_subproject'][category][subproject_name] = task_count
            
            stats['by_category'][category] = category_total
            stats['total_tasks'] += category_total
        
        return stats
    
    def _generate_markdown(
        self,
        summary: str,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date,
        stats: Dict[str, Any]
    ) -> str:
        """Génère le contenu Markdown du résumé"""
        
        md = f"""# Résumé hebdomadaire - Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}

*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*

---

## 📝 Résumé

{summary}

---

## 📊 Statistiques

- **Total de tâches complétées** : {stats['total_tasks']}
"""
        
        # Statistiques par catégorie
        for category, count in stats['by_category'].items():
            md += f"- **{category}** : {count} tâches\n"
            
            # Sous-projets si disponibles
            if category in stats['by_subproject'] and stats['by_subproject'][category]:
                for subproject, subcount in stats['by_subproject'][category].items():
                    md += f"  - {subproject}: {subcount} tâches\n"
        
        md += "\n---\n\n## 📋 Détail des tâches\n\n"
        
        # Liste des tâches par catégorie et sous-projet
        for category, subprojects in organized_tasks.items():
            md += f"### {category}\n\n"
            
            for subproject_name, tasks in subprojects.items():
                if subproject_name:
                    md += f"#### {subproject_name}\n\n"
                
                for task in tasks:
                    section = f" *({task['section_name']})*" if task.get('section_name') else ""
                    completed = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                    date_str = completed.strftime('%d/%m à %H:%M')
                    md += f"- {task['content']}{section} - ✓ {date_str}\n"
                
                md += "\n"
        
        return md
    
    def load_previous_summaries(self, weeks: int = 4) -> List[Dict[str, Any]]:
        """
        Charge les N derniers résumés pour fournir du contexte
        
        Args:
            weeks: Nombre de semaines à charger
        
        Returns:
            Liste des résumés triés du plus ancien au plus récent
        """
        json_files = sorted(self.data_dir.glob("summary_*.json"))
        
        if not json_files:
            logger.info("  Aucun résumé précédent trouvé")
            return []
        
        # Chargement des N derniers fichiers
        recent_files = json_files[-weeks:] if len(json_files) > weeks else json_files
        
        summaries = []
        for file_path in recent_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    summaries.append({
                        'week_start': data['week_start'],
                        'week_end': data['week_end'],
                        'summary': data['summary']
                    })
            except Exception as e:
                logger.warning(f"  Impossible de charger {file_path.name}: {str(e)}")
        
        logger.info(f"  {len(summaries)} résumés précédents chargés")
        return summaries
