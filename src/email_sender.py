"""
Email sender module
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from src.i18n import get_i18n

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles sending summaries via email"""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('EMAIL_TO')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.i18n = get_i18n()
        
        # Validate configuration
        if not all([self.email_from, self.email_to, self.smtp_password]):
            raise ValueError(
                "Incomplete email configuration. Check EMAIL_FROM, "
                "EMAIL_TO and SMTP_PASSWORD in .env"
            )
        
        logger.info(f"Email configuration: {self.email_from} -> {self.email_to}")
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert Markdown to HTML (simple conversion for email)
        Handles: ##, ###, paragraphs, line breaks
        """
        html = ""
        lines = markdown_text.split('\n')
        in_paragraph = False
        current_paragraph = []
        
        for line in lines:
            stripped = line.strip()
            
            # H2 heading (##)
            if stripped.startswith('## ') and not stripped.startswith('### '):
                if in_paragraph:
                    html += f"<p>{'<br>'.join(current_paragraph)}</p>\n"
                    current_paragraph = []
                    in_paragraph = False
                heading_text = stripped[3:].strip()
                html += f'<h2 style="color: #667eea; margin-top: 25px; margin-bottom: 15px; font-size: 20px;">{heading_text}</h2>\n'
            
            # H3 heading (###)
            elif stripped.startswith('### '):
                if in_paragraph:
                    html += f"<p>{'<br>'.join(current_paragraph)}</p>\n"
                    current_paragraph = []
                    in_paragraph = False
                heading_text = stripped[4:].strip()
                html += f'<h3 style="color: #764ba2; margin-top: 20px; margin-bottom: 10px; font-size: 18px;">{heading_text}</h3>\n'
            
            # Empty line = end of paragraph
            elif not stripped:
                if in_paragraph:
                    html += f"<p>{'<br>'.join(current_paragraph)}</p>\n"
                    current_paragraph = []
                    in_paragraph = False
            
            # Regular text line
            else:
                in_paragraph = True
                current_paragraph.append(stripped)
        
        # Close last paragraph if any
        if in_paragraph:
            html += f"<p>{'<br>'.join(current_paragraph)}</p>\n"
        
        return html
    
    def send_summary(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> None:
        """
        Send the summary via email
        
        Args:
            summary: The summary to send
            week_start: Week start date
            week_end: Week end date
        """
        # Format dates based on language
        if self.i18n.language == 'fr':
            start_str = week_start.strftime('%d/%m')
            end_str = week_end.strftime('%d/%m/%Y')
        else:
            start_str = week_start.strftime('%m/%d')
            end_str = week_end.strftime('%m/%d/%Y')
        
        subject = self.i18n.t('email_subject', start=start_str, end=end_str)
        
        # Build message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = self.email_to
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Text version
        text_body = self._format_text_body(summary, week_start, week_end)
        
        # HTML version (prettier)
        html_body = self._format_html_body(summary, week_start, week_end)
        
        # Attach both versions
        part1 = MIMEText(text_body, 'plain', 'utf-8')
        part2 = MIMEText(html_body, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send
        try:
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"  Email sent successfully to {self.email_to}")
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
    
    def _format_text_body(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> str:
        """Format email body as plain text"""
        # Format dates based on language
        if self.i18n.language == 'fr':
            start_str = week_start.strftime('%d/%m/%Y')
            end_str = week_end.strftime('%d/%m/%Y')
            date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
        else:
            start_str = week_start.strftime('%m/%d/%Y')
            end_str = week_end.strftime('%m/%d/%Y')
            date_str = datetime.now().strftime('%m/%d/%Y at %I:%M %p')
        
        return f"""{self.i18n.t('email_greeting')}

{self.i18n.t('email_intro', start=start_str, end=end_str)}

{summary}

---
{self.i18n.t('email_footer')}
{self.i18n.t('email_generated_at', date=date_str)}
"""
    
    def _format_html_body(
        self,
        summary: str,
        week_start: datetime.date,
        week_end: datetime.date
    ) -> str:
        """Format email body as HTML"""
        
        # Format dates based on language
        if self.i18n.language == 'fr':
            start_str = week_start.strftime('%d/%m/%Y')
            end_str = week_end.strftime('%d/%m/%Y')
            date_str = datetime.now().strftime('%d/%m/%Y à %H:%M')
            header_start = week_start.strftime('%d/%m')
            header_end = end_str
        else:
            start_str = week_start.strftime('%m/%d/%Y')
            end_str = week_end.strftime('%m/%d/%Y')
            date_str = datetime.now().strftime('%m/%d/%Y at %I:%M %p')
            header_start = week_start.strftime('%m/%d')
            header_end = end_str
        
        # Convert Markdown to HTML
        html_content = self._markdown_to_html(summary)
        
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
        <h1>{self.i18n.t('email_subject', start=header_start, end=header_end)}</h1>
        <p>{self.i18n.t('email_intro', start=start_str, end=end_str)}</p>
    </div>
    
    <div class="content">
        {html_content}
    </div>
    
    <div class="footer">
        <p>{self.i18n.t('email_footer')}</p>
        <p>{self.i18n.t('email_generated_at', date=date_str)}</p>
    </div>
</body>
</html>
"""