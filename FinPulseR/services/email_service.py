import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


class EmailSender:
    def __init__(self, sender_email, sender_password):
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(self, recipient_email, subject, message_body, is_html=False, inline_images=None):
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Attach the message body
            body_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(message_body, body_type))

            # Attach inline images if provided
            if inline_images:
                for cid, image_data in inline_images.items():
                    image = MIMEImage(image_data, name=f"{cid}.png")
                    image.add_header('Content-ID', f"<{cid}>")
                    msg.attach(image)

            # Connect to the SMTP server
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Start TLS encryption
                server.login(self.sender_email, self.sender_password)  # Log in to the SMTP server

                # Send the email
                server.send_message(msg)
                print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
