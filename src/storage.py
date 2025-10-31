"""
Local storage manager for summaries
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.i18n import get_i18n

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages saving and loading of summaries"""
    
    def __init__(self):
        self.data_dir = Path("data/summaries")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.i18n = get_i18n()
        logger.info(f"Storage directory: {self.data_dir.absolute()}")
    
    def save_summary(
        self,
        summary: str,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date
    ) -> None:
        """
        Save the summary in JSON and Markdown format
        
        Args:
            summary: The generated summary
            organized_tasks: Tasks organized by category and subproject
            week_start: Week start date
            week_end: Week end date
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        week_str = f"{week_start.strftime('%Y%m%d')}-{week_end.strftime('%Y%m%d')}"
        
        # Calculate statistics
        stats = self._calculate_stats(organized_tasks)
        
        # Prepare data
        data = {
            'generated_at': datetime.now().isoformat(),
            'week_start': week_start.isoformat(),
            'week_end': week_end.isoformat(),
            'summary': summary,
            'tasks': organized_tasks,
            'stats': stats
        }
        
        # Save JSON
        json_file = self.data_dir / f"summary_{week_str}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"  Saved: {json_file.name}")
        
        # Save Markdown (more readable)
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
        logger.info(f"  Saved: {md_file.name}")
    
    def _calculate_stats(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]]
    ) -> Dict[str, Any]:
        """Calculate task statistics"""
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
        """Generate Markdown content of the summary"""
        
        # Format dates based on language
        if self.i18n.language == 'fr':
            start_str = week_start.strftime('%d/%m/%Y')
            end_str = week_end.strftime('%d/%m/%Y')
            date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        else:
            start_str = week_start.strftime('%m/%d/%Y')
            end_str = week_end.strftime('%m/%d/%Y')
            date_str = datetime.now().strftime('%m/%d/%Y at %H:%M')
        
        md = f"""# {self.i18n.t('md_weekly_summary', start=start_str, end=end_str)}

*{self.i18n.t('md_generated_on', date=date_str)}*

---

## {self.i18n.t('md_summary_title')}

{summary}

---

## {self.i18n.t('md_stats_title')}

{self.i18n.t('md_total_tasks', count=stats['total_tasks'])}
"""
        
        # Statistics by category
        for category, count in stats['by_category'].items():
            md += f"- **{category}**: {count} tasks\n"
            
            # Subprojects if available
            if category in stats['by_subproject'] and stats['by_subproject'][category]:
                for subproject, subcount in stats['by_subproject'][category].items():
                    md += f"  - {subproject}: {subcount} tasks\n"
        
        md += f"\n---\n\n## {self.i18n.t('md_tasks_detail')}\n\n"
        
        # Task list by category and subproject
        for category, subprojects in organized_tasks.items():
            md += f"### {category}\n\n"
            
            for subproject_name, tasks in subprojects.items():
                if subproject_name:
                    md += f"#### {subproject_name}\n\n"
                
                for task in tasks:
                    section = f" *({task['section_name']})*" if task.get('section_name') else ""
                    completed = datetime.fromisoformat(task['completed_at'].replace('Z', '+00:00'))
                    
                    if self.i18n.language == 'fr':
                        date_str = completed.strftime('%d/%m à %H:%M')
                    else:
                        date_str = completed.strftime('%m/%d at %I:%M %p')
                    
                    md += f"- {task['content']}{section} - ✓ {date_str}\n"
                
                md += "\n"
        
        return md
    
    def load_previous_summaries(self, weeks: int = 4) -> List[Dict[str, Any]]:
        """
        Load the last N summaries to provide context
        
        Args:
            weeks: Number of weeks to load
        
        Returns:
            List of summaries sorted from oldest to newest
        """
        json_files = sorted(self.data_dir.glob("summary_*.json"))
        
        if not json_files:
            logger.info("  No previous summaries found")
            return []
        
        # Load last N files
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
                logger.warning(f"  Unable to load {file_path.name}: {str(e)}")
        
        logger.info(f"  {len(summaries)} previous summaries loaded")
        return summaries