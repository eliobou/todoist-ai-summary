"""
Todoist AI Summary - Main entry point
Generates weekly summaries of completed Todoist tasks
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
from src.i18n import get_i18n


def setup_logging():
    """Configure logging system"""
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
    """Return start and end dates of past week (Monday-Sunday)"""
    today = datetime.now().date()
    # Sunday = 6, we want to go back to previous Monday
    days_since_monday = (today.weekday() + 1) % 7
    if days_since_monday == 0:  # If it's Sunday
        days_since_monday = 7
    
    start_date = today - timedelta(days=days_since_monday)
    end_date = start_date + timedelta(days=6)
    
    return start_date, end_date


def main():
    """Main function"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logging()
    
    # Get i18n instance
    i18n = get_i18n()
    
    logger.info("=" * 80)
    logger.info(i18n.t('log_startup'))
    logger.info("=" * 80)
    
    try:
        # Get week range
        start_date, end_date = get_week_range()
        logger.info(i18n.t('log_period', start=start_date, end=end_date))
        
        # 1. Fetch tasks from Todoist
        logger.info(i18n.t('log_step', step=1, total=5, action=i18n.t('log_connecting_todoist')))
        todoist = TodoistClient()
        completed_tasks = todoist.get_completed_tasks(start_date, end_date)
        logger.info(f"✓ {i18n.t('log_tasks_found', count=len(completed_tasks))}")
        
        if not completed_tasks:
            logger.warning(i18n.t('log_no_tasks'))
            return
        
        # 2. Organize tasks by category
        logger.info(i18n.t('log_step', step=2, total=5, action=i18n.t('log_organizing_tasks')))
        organized_tasks = todoist.organize_tasks_by_category(completed_tasks)
        
        for category, subprojects in organized_tasks.items():
            total = sum(len(tasks) for tasks in subprojects.values())
            logger.info(f"  - {category}: {total} tasks")
        
        # 3. Generate summary with OpenAI
        logger.info(i18n.t('log_step', step=3, total=5, action=i18n.t('log_generating_summary')))
        summarizer = WeeklySummarizer()
        
        # Load context from previous weeks
        storage = StorageManager()
        previous_summaries = storage.load_previous_summaries(
            weeks=int(os.getenv('WEEKS_OF_CONTEXT', '4'))
        )
        
        if previous_summaries:
            logger.info(f"  - {i18n.t('log_context_loaded', count=len(previous_summaries))}")
        
        summary = summarizer.generate_summary(
            organized_tasks=organized_tasks,
            week_start=start_date,
            week_end=end_date,
            previous_summaries=previous_summaries
        )
        logger.info(f"✓ {i18n.t('log_summary_generated')}")
        
        # 4. Save locally
        logger.info(i18n.t('log_step', step=4, total=5, action=i18n.t('log_saving_local')))
        storage.save_summary(
            summary=summary,
            organized_tasks=organized_tasks,
            week_start=start_date,
            week_end=end_date
        )
        logger.info(f"✓ {i18n.t('log_summary_saved')}")
        
        # 5. Send email
        if os.getenv('EMAIL_SEND', False):
            logger.info(i18n.t('log_step', step=5, total=5, action=i18n.t('log_sending_email')))
            email_sender = EmailSender()
            email_sender.send_summary(
                summary=summary,
                week_start=start_date,
                week_end=end_date
            )
            logger.info(f"✓ {i18n.t('log_email_sent')}")
            
            logger.info("=" * 80)
            logger.info(i18n.t('log_script_complete'))
            logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"❌ {i18n.t('log_error')}: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()