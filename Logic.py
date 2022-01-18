import copy
import collections
from datetime import datetime
from TelegramApi import TelegramApi


class Logic:
    
    def __init__(self, config, logging):
        self.config = config
        self.telegram = TelegramApi(config, logging)
        self.logging = logging

    def validators_comparison(self, actual, old, block):
        temp_actual = copy.copy(actual)
        temp_old = copy.copy(old)

        if collections.Counter(actual) == collections.Counter(old):
            self.logging.info('Without changes - {}'.format(block))
            return False

        if collections.Counter(actual) != collections.Counter(old):
            for i in old:
                for k in actual:
                    if i == k:
                        temp_old.remove(k)
                        temp_actual.remove(k)
        return [temp_actual, temp_old]

    def remove_online(self, validators_list, to_check):
        items = copy.copy(to_check)
        for validator in to_check:
            if any(validators_list for i in validators_list if i['moniker'] == validator and i['status'] == 'online'):
                items.discard(validator)
                self.logging.info("Валидатор {} пропал из блока но все еще онлайн".format(validator))

        return items

    def print_status(self, block, old, actual):
        now = datetime.utcnow()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        if old:
            for i in old:
                message = 'Валидатор *{}* выключен на блоке *#{}*\n{} UTC'.format(i, block, dt_string, dt_string)
                self.telegram.text = message
                self.telegram.send_notify()
                self.telegram.text = None

        if actual:
            for k in actual:
                message = 'Валидатор *{}* включен на блоке *#{}*\n{} UTC'.format(k, block, dt_string, dt_string)
                self.telegram.text = message
                self.telegram.send_notify()
                self.telegram.text = None

    def print_slashes(self, moniker, block):
        now = datetime.utcnow()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        message = 'Валидатор *{}* получил штраф на блоке *#{}*\n{} UTC'.format(moniker, block, dt_string)
        self.telegram.text = message
        self.telegram.send_notify()
        self.telegram.text = None
