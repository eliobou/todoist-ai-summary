"""
AI summary generator with OpenAI
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import openai
from openai import OpenAI
from src.i18n import get_i18n

logger = logging.getLogger(__name__)


class WeeklySummarizer:
    """Generates weekly summaries with OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY missing in .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.i18n = get_i18n()
        
        logger.info(f"Initializing OpenAI with model {self.model}")
    
    def _build_prompt(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date,
        previous_summaries: List[Dict[str, Any]]
    ) -> str:
        """Build the prompt for OpenAI"""
        
        # Format dates based on language
        if self.i18n.language == 'fr':
            start_str = week_start.strftime('%d/%m/%Y')
            end_str = week_end.strftime('%d/%m/%Y')
        else:
            start_str = week_start.strftime('%m/%d/%Y')
            end_str = week_end.strftime('%m/%d/%Y')
        
        # Header
        prompt = f"{self.i18n.t('prompt_system')}\n\n"
        prompt += f"{self.i18n.t('prompt_period', start=start_str, end=end_str)}\n\n"
        
        # Context from previous weeks (if available)
        if previous_summaries:
            prompt += f"{self.i18n.t('prompt_context')}\n"
            for summary in previous_summaries[-4:]:  # Max 4 weeks
                week_info = f"{summary['week_start']} to {summary['week_end']}"
                prompt += f"\n--- Week of {week_info} ---\n"
                prompt += summary['summary'] + "\n"
            prompt += "\n"
        
        # Completed tasks this week
        prompt += f"{self.i18n.t('prompt_tasks')}\n\n"
        
        # For each category (Work, Perso, Tinker...)
        for category, subprojects in organized_tasks.items():
            prompt += f"=== {category.upper()} ===\n"
            
            # For each subproject
            for subproject_name, tasks in subprojects.items():
                if subproject_name:
                    prompt += f"\n{self.i18n.t('prompt_subproject', name=subproject_name)}\n"
                
                for task in tasks:
                    section = f" (section: {task['section_name']})" if task.get('section_name') else ""
                    prompt += f"- {task['content']}{section}\n"
                
                if not subproject_name:
                    # If no subproject, add blank line
                    prompt += "\n"
            
            prompt += "\n"
        
        # Generation instructions
        prompt += f"\n{self.i18n.t('prompt_instructions')}:\n"
        prompt += f"{self.i18n.t('prompt_instruction_text')}\n\n"
        prompt += f"{self.i18n.t('prompt_format')}\n"
        
        # Dynamically build expected structure
        for category in organized_tasks.keys():
            prompt += f"\n## {category}\n"
            
            subprojects = organized_tasks[category]
            has_subprojects = any(sp is not None for sp in subprojects.keys())
            
            if has_subprojects:
                prompt += "\nFor each subproject with tasks:\n"
                for subproject_name in subprojects.keys():
                    if subproject_name:
                        prompt += f"### {subproject_name}\n"
                        prompt += "[Paragraph describing tasks for this subproject]\n\n"
            else:
                prompt += "[Paragraph describing tasks]\n\n"
        
        prompt += f"\n{self.i18n.t('prompt_style')}\n"
        prompt += f"{self.i18n.t('prompt_style_rules')}\n\n"
        
        prompt += f"{self.i18n.t('prompt_important')}\n"
        prompt += f"{self.i18n.t('prompt_important_rules')}\n\n"
        
        prompt += f"{self.i18n.t('prompt_request')}\n"
        
        return prompt
    
    def generate_summary(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date,
        previous_summaries: List[Dict[str, Any]] = None
    ) -> str:
        """
        Generate the weekly summary
        
        Args:
            organized_tasks: Tasks organized by category and subproject
            week_start: Week start date
            week_end: Week end date
            previous_summaries: Previous weeks' summaries for context
        
        Returns:
            The generated summary
        """
        if previous_summaries is None:
            previous_summaries = []
        
        logger.info("Building prompt...")
        prompt = self._build_prompt(
            organized_tasks=organized_tasks,
            week_start=week_start,
            week_end=week_end,
            previous_summaries=previous_summaries
        )
        
        logger.info(f"Calling OpenAI API (model: {self.model})...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.i18n.t('prompt_system')
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Reduced for more factuality
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Log usage stats
            usage = response.usage
            logger.info(f"  Tokens used - Input: {usage.prompt_tokens}, "
                       f"Output: {usage.completion_tokens}, "
                       f"Total: {usage.total_tokens}")
            
            # Cost estimation (approximate prices for gpt-4o-mini)
            input_cost = usage.prompt_tokens * 0.00015 / 1000
            output_cost = usage.completion_tokens * 0.0006 / 1000
            total_cost = input_cost + output_cost
            logger.info(f"  Estimated cost: ${total_cost:.6f}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            raise