import yagmail
import os
import logging

log = logging.getLogger()

def send_email(app_password: str, number_carrier_hostname: str, message: str) -> None:

    GMAIL_USER = "codys.automated.email@gmail.com"

    yag = yagmail.SMTP(GMAIL_USER, app_password)
    
    yag.send(
        to= number_carrier_hostname, 
        subject='Codys Simple Stock Notifier', 
        contents=message
    )

    log.info("Sent email")

