import smtplib
import json
from email.message import EmailMessage

with open('stats.json', 'r') as fr:
    data = json.load(fr)

msg = EmailMessage()
msg["From"] = 'ml.stats.python@gmail.com'
msg["Subject"] = "Test mail"
msg["To"] = 'adam.pankuch@gmail.com'
msg.set_content("This is the message body")
msg.add_attachment(json.dumps(data, indent=4), filename="stats.json")

s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
s.ehlo()
s.login('ml.stats.python@gmail.com', 'Python4ever')
s.send_message(msg)
s.quit()



