import requests
import time


class TelegramApi:
    text = None

    def __init__(self, config, logging):
        self.method = config['telegram']['api_url'] + config['telegram']['token'] + "/sendMessage"
        self.channel_id = config['telegram']['channel_id']
        self.logging = logging

    def send_notify(self):
        if self.text is not None:
            for i in range(5):
                try:
                    request = requests.post(self.method, data={
                        "chat_id": self.channel_id,
                        "text": self.text,
                        "parse_mode": 'markdown'
                    })
                    time.sleep(0.5)

                    if request.status_code != 200:
                        self.logging.error(
                            "Error send telegram message, code: {0}, try number {1}".format(request.status_code, i + 1))
                        time.sleep(1.5)
                        continue

                    self.logging.info("Sent notify into Telegram with text: {0}".format(self.text))
                    return True

                except requests.exceptions.RequestException as err:
                    self.logging.error(err)
                    continue
