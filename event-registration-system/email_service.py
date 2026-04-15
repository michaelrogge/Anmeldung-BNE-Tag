import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging
from threading import Thread

logger = logging.getLogger(__name__)

class EmailService:
    """Service für Email-Versand"""
    
    @staticmethod
    def send_async(app, msg):
        """Sendet Email asynchron"""
        with app.app_context():
            try:
                smtp = smtplib.SMTP(
                    current_app.config['MAIL_SERVER'],
                    current_app.config['MAIL_PORT']
                )
                smtp.starttls()
                smtp.login(
                    current_app.config['MAIL_USERNAME'],
                    current_app.config['MAIL_PASSWORD']
                )
                smtp.send_message(msg)
                smtp.quit()
                logger.info(f"Email erfolgreich an {msg['To']} versendet")
            except Exception as e:
                logger.error(f"Email-Fehler an {msg['To']}: {str(e)}")
    
    @staticmethod
    def send_email(to_email, subject, html_content, text_content=None):
        """Sendet Email mit HTML"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(part2)
            
            # Asynchron versenden
            thread = Thread(
                target=EmailService.send_async,
                args=(current_app._get_current_object(), msg)
            )
            thread.daemon = True
            thread.start()
            
            return True
        except Exception as e:
            logger.error(f"Fehler beim Versand an {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_confirmation_email(participant, event, workshops):
        """Sendet Teilnahmebestätigung"""
        workshop_list = '<ul>' + ''.join(
            f'<li>{w.name} ({w.start_time.strftime("%d.%m.%Y, %H:%M") if w.start_time else "TBD"})</li>'
            for w in workshops
        ) + '</ul>'
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>Teilnahmebestätigung</h2>
                
                <p>Lieber {participant.first_name},</p>
                
                <p>vielen Dank für Ihre Anmeldung zur Veranstaltung <strong>{event.name}</strong>!</p>
                
                <p><strong>Ihre Workshops:</strong></p>
                {workshop_list}
                
                <p><strong>Veranstaltungsinformationen:</strong></p>
                <ul>
                    <li><strong>Datum:</strong> {event.date.strftime('%d.%m.%Y, %H:%M')}</li>
                    <li><strong>Ort:</strong> {event.location or 'Wird noch bekannt gegeben'}</li>
                </ul>
                
                <p>Sollten Sie Fragen haben, antworten Sie gerne auf diese Email.</p>
                
                <p>Mit freundlichen Grüßen,<br>
                Das Veranstaltungsteam</p>
            </body>
        </html>
        """
        
        text_content = f"""
        Teilnahmebestätigung
        
        Lieber {participant.first_name},
        
        vielen Dank für Ihre Anmeldung zur Veranstaltung {event.name}!
        
        Ihre Workshops:
        {', '.join(w.name for w in workshops)}
        
        Veranstaltungsinformationen:
        Datum: {event.date.strftime('%d.%m.%Y, %H:%M')}
        Ort: {event.location or 'Wird noch bekannt gegeben'}
        """
        
        return EmailService.send_email(
            participant.email,
            f"Teilnahmebestätigung: {event.name}",
            html_content,
            text_content
        )
    
    @staticmethod
    def send_bulk_confirmations(registrations):
        """Sendet Bestätigungen an mehrere Teilnehmer"""
        success_count = 0
        for registration in registrations:
            if EmailService.send_confirmation_email(
                registration.participant,
                registration.event,
                [wr.workshop for wr in registration.workshop_selections]
            ):
                success_count += 1
        
        return success_count, len(registrations)
    
    @staticmethod
    def send_notification(admin_email, subject, message):
        """Sendet Benachrichtigung an Admin"""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>{subject}</h2>
                <p>{message}</p>
            </body>
        </html>
        """
        
        return EmailService.send_email(
            admin_email,
            f"Benachrichtigung: {subject}",
            html_content
        )
