import requests
import logging

log = logging.getLogger()

def send_telegram(token: str, chat_id: str, message: str, url: str):

    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}\n{url}"
    response = requests.get(url)
    log.info("Sent to Telegram.")