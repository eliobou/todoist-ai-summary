"""
Gestionnaire d'envoi d'emails
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    """Gère l'envoi des résumés par email"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Validation de la configuration
        if not all([self.email_from, self.email_to, self.smtp_password]):
            raise ValueError(
                "Configuration email incomplète. Vérifiez EMAIL_FROM, "
                "EMAIL_TO et SMTP_PASSWORD dans .env"
            )
        
        logger.info(f"Configuration email : {self.email_from} -> {self.email_to}")
    
    def send_summary(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> None:
        """
        Envoie le résumé par email
        
        Args:
            summary: Le résumé à envoyer
            week_start: Date de début de semaine
            week_end: Date de fin de semaine
        """
        subject = f"📊 Résumé hebdomadaire - Semaine du {week_start.strftime('%d/%m')} au {week_end.strftime('%d/%m/%Y')}"
        
        # Construction du message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Version texte
        text_body = self._format_text_body(summary, week_start, week_end)
        
        # Version HTML (plus jolie)
        html_body = self._format_html_body(summary, week_start, week_end)
        
        # Attachement des deux versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Envoi
        try:
            logger.info(f"Connexion à {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"  Email envoyé avec succès à {self.email_to}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            raise
    
    def _format_text_body(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> str:
        """Formate le corps de l'email en texte brut"""
        return f"""Bonjour,

Voici ton résumé hebdomadaire pour la semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}.

{summary}

---
Ce résumé a été généré automatiquement par Todoist AI Summary.
Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}
"""
    
    def _format_html_body(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> str:
        """Formate le corps de l'email en HTML"""
        
        # Conversion des retours à la ligne en paragraphes HTML
        paragraphs = summary.split('\n\n')
        html_paragraphs = ''.join(f'<p>{p.replace(chr(10), "<br>")}</p>' for p in paragraphs if p.strip())
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 24px;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .content p {{
            margin: 0 0 15px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 12px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Résumé hebdomadaire</h1>
        <p>Semaine du {week_start.strftime('%d/%m/%Y')} au {week_end.strftime('%d/%m/%Y')}</p>
    </div>
    
    <div class="content">
        {html_paragraphs}
    </div>
    
    <div class="footer">
        <p>Ce résumé a été généré automatiquement par <strong>Todoist AI Summary</strong></p>
        <p>Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</p>
    </div>
</body>
</html>
"""
