from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import os

from secrets import CONFIG

class SendMail(object):
    "Send mail to my address"
    def __init__(self):
        self.user = CONFIG['email_from']
        self.password = CONFIG['email_pass']

    def send(self, zip_file_path):
        "Actually send the message"
        msg = MIMEMultipart()
        msg["Subject"] = CONFIG['email_title']
        msg["From"] = CONFIG['email_from']
        msg["To"] = CONFIG['email_to']

        attach_file = MIMEBase('application', 'zip')
        attach_file.set_payload(open(zip_file_path).read())

        Encoders.encode_base64(attach_file)
        attach_file.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(zip_file_path))
        msg.attach(attach_file)

        body = MIMEText(CONFIG['email_body'])
        msg.attach(body)

        smtp = SMTP()
        smtp.connect(CONFIG['email_server_port'])
        smtp.starttls()
        smtp.login(self.user, self.password)
        smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        smtp.quit()
