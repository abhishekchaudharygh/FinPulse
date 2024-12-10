import os
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from email.mime.text import MIMEText
from fastapi import HTTPException
from pydantic import BaseModel

# Load environment variables
OWN_EMAIL = os.getenv('MY_EMAIL')
OWN_EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


class EmailBody(BaseModel):
    to: str
    subject: str
    message: str


async def send_email(body: EmailBody):
    try:
        # Create message
        msg = MIMEText(body.message, "html")
        msg['Subject'] = body.subject
        msg['From'] = f'Denolyrics <{OWN_EMAIL}>'
        msg['To'] = body.to

        # Use SMTP server settings
        smtp_server = "mail.privateemail.com"
        port = 587  # For TLS
        server = SMTP(smtp_server, port)
        server.starttls()  # Start TLS for secure connection

        # Authenticate and send the email
        try:
            server.login(OWN_EMAIL, OWN_EMAIL_PASSWORD)
        except SMTPAuthenticationError as auth_error:
            raise HTTPException(status_code=500, detail=f"Authentication failed: {auth_error}")
        except SMTPException as smtp_error:
            raise HTTPException(status_code=500, detail=f"SMTP error: {smtp_error}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        # Send the email
        server.send_message(msg)
        server.quit()  # Close the connection
        return {"message": "Email sent successfully"}

    except Exception as e:
        # Return HTTPException with string representation of error
        raise HTTPException(status_code=500, detail=str(e))
