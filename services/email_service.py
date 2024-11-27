# email_utils.py
from config import Config
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
import logging
# from reportlab.lib.styles import getSampleStyleSheet
# styles = getSampleStyleSheet()

from azure.communication.email import EmailClient
from config import Config
import logging

import logging
from azure.communication.email import EmailClient

def send_email(to_email, subject, html_content,attachment=None):
    try:
        # Initialize EmailClient
        email_client = EmailClient.from_connection_string(Config.COMMUNICATION_SERVICE_CONNECTION_STRING)

        # Log the sender email for verification

        # Prepare the email message
        email_message = {
            "senderAddress": Config.FROM_AZURE_EMAIL,  # Make sure this is the verified sender address
            "content": {
                "subject": subject,
                "html": html_content
            },
            "recipients": {
                "to": [{"address": to_email}]
            }
        }


        if attachment:
            email_message['attachments'] = [attachment]
        # Start the send email operation
        poller = email_client.begin_send(email_message)
        response = poller.result()

        # Check for success
        if hasattr(response, 'message_id') and response.message_id:
            return {'status': 'Email sent successfully', 'message_id': response.message_id}
        else:
            return {'status': 'Failed to send email', 'error': "No Message ID returned"}

    except Exception as e:
        return {'status': 'Failed to send email', 'error': str(e)}

