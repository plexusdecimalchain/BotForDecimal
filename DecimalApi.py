import requests
import time
from RequestsRetry import requests_retry_session


class DecimalApi:
    old_block = 0
    actual_block = 0
    actual_validator_list = None
    old_validators_list = None
    count = None
    session = None

    def __init__(self, session, config, logging):
        self.config = config
        self.url = config['decimal']['api_url']
        self.session = session
        self.logging = logging

    def validators_count(self):
        return requests_retry_session().get("{}/validators/validator".format(self.url),
                                            params={'offset': 0, 'order[stake]': 'DESC', 'limit': 0}).json()['result'][
            'count']

    def validators_list(self, count):
        return requests_retry_session().get("{}/validators/validator".format(self.url),
                                            params={'offset': 0, 'order[stake]': 'DESC', 'limit': count}).json()[
            'result'][
            'validators']

    def block(self):
        url = self.url + '/block/height'
        return int(requests_retry_session().get(url).json()) - 5

    def validator_list(self, block, session):
        for i in range(5):
            try:
                validators_response = session.get(
                    '{0}/block/{1}/validators'.format(self.url, block))

                if validators_response.status_code != 200:
                    self.logging.error(
                        "Error receiving validator list, code: {0}, try number {1}".format(validators_response
                                                                                           .status_code, i + 1))
                    time.sleep(1)
                    continue

                if len(validators_response.json()['result']['validators']) < 1:
                    self.logging.error('Not valid response from last request, retrying...')
                    time.sleep(1)
                    continue

                validators = set()

                for validator in validators_response.json()['result']['validators']:
                    validators.add(validator['validator']['moniker'])
                return validators

            except requests.exceptions.RequestException as err:
                self.logging.error(err)
                return False

    def slashes(self, limit, offset, session):
        for i in range(5):
            try:

                slashes_response = session.get(
                    '{0}/slashes'
                    '?limit={1}&offset={2}&order[blockId]=DESC'.format(self.url, limit, offset))

                if slashes_response.status_code != 200:
                    self.logging.error("Error receiving validator list, code: {0}, try number {1}"
                                       .format(slashes_response.status_code, i + 1))
                    time.sleep(0.5)
                    continue

                if len(slashes_response.json()) < 1:
                    self.logging.error('Not valid response with slashes from last request, retrying...')
                    time.sleep(0.5)
                    continue

                return slashes_response.json()

            except requests.exceptions.RequestException as err:
                self.logging.error(err)
                return False
