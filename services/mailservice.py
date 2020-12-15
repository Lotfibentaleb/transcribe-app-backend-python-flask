from app import app
import requests
from settings import MAILGUN_DOMAIN, MAILGUN_KEY, MAILGUN_FROM_ADDRESS

app.config['MAILGUN_KEY'] = MAILGUN_KEY
app.config['MAILGUN_DOMAIN'] = MAILGUN_DOMAIN
app.config['MAIL_FROM_ADDRESS'] = MAILGUN_FROM_ADDRESS

def send_mail(to_address, subject, plaintext, html):
    print(to_address)
    print(subject)
    print(app.config['MAIL_FROM_ADDRESS'])
    print(html)
    r = requests.\
        post("https://api.mailgun.net/v2/%s/messages" % app.config['MAILGUN_DOMAIN'],
            auth=("api", app.config['MAILGUN_KEY']),
             data={
                 "from": app.config['MAIL_FROM_ADDRESS'],
                 "to": to_address,
                 "subject": subject,
                 "text": plaintext,
                 "html": html
             }
         )
    return r
