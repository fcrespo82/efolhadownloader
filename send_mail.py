from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import Encoders
import os

class SendMail(object):
    "Send mail to my address"
    def __init__(self):
        self.user = 'fernando82@gmail.com'
        self.password = 'xudqowlckgtlrceq'

    def send(self, zip_file_path):
        "Actually send the message"
        msg = MIMEMultipart()
        msg["Subject"] = "Demonstrativo de pagamento"
        msg["From"] = 'fernando82@gmail.com'
        msg["To"] = 'fernando82@gmail.com'

        attach_file = MIMEBase('application', 'zip')
        attach_file.set_payload(open(zip_file_path).read())

        Encoders.encode_base64(attach_file)
        attach_file.add_header('Content-Disposition', 'attachment',
                               filename=os.path.basename(zip_file_path))
        msg.attach(attach_file)

        body = MIMEText("Segue comprovantes de pagamento")
        msg.attach(body)

        smtp = SMTP()
        smtp.connect('smtp.gmail.com:587')
        smtp.starttls()
        smtp.login(self.user, self.password)
        smtp.sendmail(msg["From"], msg["To"], msg.as_string())
        smtp.quit()
