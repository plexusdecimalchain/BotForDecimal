from time import sleep
import time
import requests
import copy
import configparser
import logging
from datetime import datetime
from DecimalApi import DecimalApi
from Logic import Logic


def main():
    config = configparser.ConfigParser()
    config.read_file(open("settings.ini"))
    session = requests.Session()
    logging.basicConfig(level=logging.INFO)

    api = DecimalApi(session, config, logging)
    logic = Logic(config, logging)

    logging.info('Bot started - {} for api {}'.format(datetime.utcnow(), api.url))

    def run():
        slashes_object = None

        while True:
            api.actual_block = api.block()

            if int(api.actual_block) > int(api.old_block) + 1 and api.old_block != 0:
                api.actual_block = int(api.old_block) + 1

            if int(api.actual_block) == int(api.old_block):
                time.sleep(1)
                continue

            logging.info('Block to checking: {}'.format(api.actual_block))

            if api.actual_block:
                api.actual_validator_list = api.validator_list(api.actual_block, session)

            if slashes_object is None:
                slashes_object = api.slashes(len(api.actual_validator_list), 0, session)
                slashes_object = slashes_object['result']['slashes']

            if api.old_validators_list is None:
                api.old_validators_list = copy.copy(api.actual_validator_list)

            if api.actual_validator_list:
                status = logic.validators_comparison(api.actual_validator_list, api.old_validators_list,
                                                     api.actual_block)
                if status:
                    if status[1]:
                        sleep(1)
                        validators_list = api.validators_list(api.validators_count())
                        status[1] = logic.remove_online(validators_list, status[1])

                    if status[1] != status[0]:
                        logic.print_status(api.actual_block, actual=status[0], old=status[1])

                    if status[1]:
                        temp = api.slashes(len(slashes_object), 0, session)
                        temp = temp['result']['slashes']

                        if temp != slashes_object:
                            for i in temp:
                                if i not in slashes_object:
                                    logic.print_slashes(i['validator']['moniker'], i['blockId'])

                        slashes_object = None

                    api.old_validators_list = copy.copy(api.actual_validator_list.difference_update(status[1]))

            api.old_block = api.actual_block

    run()


if __name__ == '__main__':
    main()
