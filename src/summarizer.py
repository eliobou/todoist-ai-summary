"""
Générateur de résumés hebdomadaires avec OpenAI
"""

import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class WeeklySummarizer:
    """Génère des résumés hebdomadaires avec OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY manquant dans .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        logger.info(f"Initialisation de OpenAI avec le modèle {self.model}")
    
    def _build_prompt(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date,
        previous_summaries: List[Dict[str, Any]]
    ) -> str:
        """Construit le prompt pour OpenAI"""
        
        # En-tête
        prompt = f"""Tu es un assistant qui aide à rédiger des résumés hebdomadaires personnels.

PÉRIODE : Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}

"""
        
        # Contexte des semaines précédentes (si disponible)
        if previous_summaries:
            prompt += "CONTEXTE (semaines précédentes) :\n"
            for summary in previous_summaries[-4:]:  # Max 4 semaines
                week_info = f"{summary['week_start']} au {summary['week_end']}"
                prompt += f"\n--- Semaine du {week_info} ---\n"
                prompt += summary['summary'] + "\n"
            prompt += "\n"
        
        # Tâches complétées cette semaine
        prompt += "TÂCHES COMPLÉTÉES CETTE SEMAINE :\n\n"
        
        # Pour chaque catégorie (ECL, Perso, Tinker...)
        for category, subprojects in organized_tasks.items():
            prompt += f"=== {category.upper()} ===\n"
            
            # Pour chaque sous-projet
            for subproject_name, tasks in subprojects.items():
                if subproject_name:
                    prompt += f"\n[Sous-projet: {subproject_name}]\n"
                
                for task in tasks:
                    section = f" (section: {task['section_name']})" if task.get('section_name') else ""
                    prompt += f"- {task['content']}{section}\n"
                
                if not subproject_name:
                    # Si pas de sous-projet, ajouter une ligne vide
                    prompt += "\n"
            
            prompt += "\n"
        
        # Instructions de génération
        prompt += f"""
INSTRUCTIONS :
Rédige un résumé de ma semaine en te basant UNIQUEMENT sur les tâches complétées ci-dessus.

FORMAT REQUIS (STRUCTURE MARKDOWN) :
"""
        
        # Construction dynamique de la structure attendue
        for category in organized_tasks.keys():
            prompt += f"\n## {category}\n"
            
            subprojects = organized_tasks[category]
            has_subprojects = any(sp is not None for sp in subprojects.keys())
            
            if has_subprojects:
                prompt += "\nPour chaque sous-projet ayant des tâches :\n"
                for subproject_name in subprojects.keys():
                    if subproject_name:
                        prompt += f"### {subproject_name}\n"
                        prompt += "[Paragraphe décrivant les tâches de ce sous-projet]\n\n"
            else:
                prompt += "[Paragraphe décrivant les tâches]\n\n"
        
        prompt += """
STYLE :
- Ton factuel et professionnel mais naturel
- À la 1ère personne ("J'ai...", "Je me suis concentré sur...")
- Pas de liste à puces, uniquement des paragraphes fluides en phrases complètes
- NE PAS extrapoler d'émotions ou de ressentis (exemple : éviter "qui m'agaçait", "pas mal de temps", etc.)
- Rester strictement factuel : décrire ce qui a été fait, pas comment je me suis senti
- Si tu as le contexte des semaines précédentes, assure une continuité narrative naturelle
- Utiliser EXACTEMENT les titres ## et ### comme indiqué ci-dessus

IMPORTANT :
- Utilise les titres Markdown (##) pour chaque catégorie principale
- Utilise les sous-titres (###) UNIQUEMENT pour les sous-projets qui existent
- Si une catégorie n'a pas de sous-projets (juste un nom de catégorie), écris directement le paragraphe sans sous-titre ###
- Chaque sous-projet doit avoir son propre paragraphe distinct sous son titre ###
- Commence directement par les titres Markdown, sans introduction

Rédige maintenant le résumé en suivant EXACTEMENT cette structure :
"""
        
        return prompt
    
    def generate_summary(
        self,
        organized_tasks: Dict[str, Dict[str, List[Dict[str, Any]]]],
        week_start: datetime.date,
        week_end: datetime.date,
        previous_summaries: List[Dict[str, Any]] = None
    ) -> str:
        """
        Génère le résumé hebdomadaire
        
        Args:
            organized_tasks: Tâches organisées par catégorie et sous-projet
            week_start: Date de début de semaine
            week_end: Date de fin de semaine
            previous_summaries: Résumés des semaines précédentes pour contexte
        
        Returns:
            Le résumé généré
        """
        if previous_summaries is None:
            previous_summaries = []
        
        logger.info("Construction du prompt...")
        prompt = self._build_prompt(
            organized_tasks=organized_tasks,
            week_start=week_start,
            week_end=week_end,
            previous_summaries=previous_summaries
        )
        
        logger.info(f"Appel à l'API OpenAI (modèle: {self.model})...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un assistant qui aide à rédiger des résumés hebdomadaires personnels de manière factuelle et structurée."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Réduit pour plus de factualité
                max_tokens=2000
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Logging des stats d'utilisation
            usage = response.usage
            logger.info(f"  Tokens utilisés - Input: {usage.prompt_tokens}, "
                       f"Output: {usage.completion_tokens}, "
                       f"Total: {usage.total_tokens}")
            
            # Estimation du coût (prix approximatifs pour gpt-4o-mini)
            input_cost = usage.prompt_tokens * 0.00015 / 1000
            output_cost = usage.completion_tokens * 0.0006 / 1000
            total_cost = input_cost + output_cost
            logger.info(f"  Coût estimé: ${total_cost:.6f}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à OpenAI: {str(e)}")
            raise
