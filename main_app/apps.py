import logging

from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = 'main_app'


class LogInfoFilter(logging.Filter):
    def filter(self, record):
        # print('******' + str(record))
        if record.funcName.find('log_message') == -1:
            # print("find!")
            return True
        return False
