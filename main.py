"""
Todoist AI Summary - Point d'entrée principal
Génère un résumé hebdomadaire des tâches Todoist complétées
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

from src.todoist_client import TodoistClient
from src.summarizer import WeeklySummarizer
from src.storage import StorageManager
from src.email_sender import EmailSender

# Configuration des logs
def setup_logging():
    """Configure le système de logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def get_week_range():
    """Retourne les dates de début et fin de la semaine écoulée (lundi-dimanche)"""
    today = datetime.now().date()
    # Dimanche = 6, on veut revenir au lundi précédent
    days_since_monday = (today.weekday() + 1) % 7
    if days_since_monday == 0:  # Si on est dimanche
        days_since_monday = 7
    
    start_date = today - timedelta(days=days_since_monday)
    end_date = start_date + timedelta(days=6)
    
    return start_date, end_date


def main():
    """Fonction principale"""
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Setup du logging
    logger = setup_logging()
    logger.info("=" * 80)
    logger.info("Démarrage du script Todoist AI Summary")
    logger.info("=" * 80)
    
    try:
        # Récupération des dates de la semaine
        start_date, end_date = get_week_range()
        logger.info(f"Période analysée : {start_date} au {end_date}")
        
        # 1. Récupération des tâches depuis Todoist
        logger.info("Étape 1/5 : Connexion à Todoist...")
        todoist = TodoistClient()
        completed_tasks = todoist.get_completed_tasks(start_date, end_date)
        logger.info(f"✓ {len(completed_tasks)} tâches complétées récupérées")
        
        if not completed_tasks:
            logger.warning("Aucune tâche complétée cette semaine. Arrêt du script.")
            return
        
        # 2. Organisation des tâches par catégorie
        logger.info("Étape 2/5 : Organisation des tâches...")
        organized_tasks = todoist.organize_tasks_by_category(completed_tasks)
        
        for category, tasks in organized_tasks.items():
            logger.info(f"  - {category}: {len(tasks)} tâches")
        
        # 3. Génération du résumé avec OpenAI
        logger.info("Étape 3/5 : Génération du résumé IA...")
        summarizer = WeeklySummarizer()
        
        # Chargement du contexte des semaines précédentes
        storage = StorageManager()
        previous_summaries = storage.load_previous_summaries(
            weeks=int(os.getenv('WEEKS_OF_CONTEXT', '4'))
        )
        
        if previous_summaries:
            logger.info(f"  - Contexte chargé : {len(previous_summaries)} semaines précédentes")
        
        summary = summarizer.generate_summary(
            organized_tasks=organized_tasks,
            week_start=start_date,
            week_end=end_date,
            previous_summaries=previous_summaries
        )
        logger.info("✓ Résumé généré avec succès")
        
        # 4. Sauvegarde locale
        logger.info("Étape 4/5 : Sauvegarde locale...")
        storage.save_summary(
            summary=summary,
            organized_tasks=organized_tasks,
            week_start=start_date,
            week_end=end_date
        )
        logger.info("✓ Résumé sauvegardé localement")
        
        # 5. Envoi par email
        if os.getenv('EMAIL_SEND'):
            logger.info("Étape 5/5 : Envoi par email...")
            email_sender = EmailSender()
            email_sender.send_summary(
                summary=summary,
                week_start=start_date,
                week_end=end_date
            )
            logger.info("✓ Email envoyé avec succès")
        
        logger.info("=" * 80)
        logger.info("Script terminé avec succès !")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution : {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
