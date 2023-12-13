import smtplib
import ssl
from email.message import EmailMessage


class Email:
    def __init__(self):
        self.email_sender = 'instamaninov@gmail.com'
        self.ema_password = 'bzaemtnlmmuwqpof'

    def sender(self, error):
        email_receiver = 'hromosoma235@gmail.com'
        subject = 'Error in site'
        em = EmailMessage()
        em['From'] = self.email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(error)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.email_sender, self.ema_password)
            smtp.sendmail(self.email_sender, email_receiver, em.as_string())
