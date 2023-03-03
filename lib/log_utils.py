import logging
from logging.handlers import RotatingFileHandler

from lib.conf_tool import http_conf

log_level_set = {'debug', 'error', 'warning', 'critical', 'info'}


def switch_log_level(log_level):
    if log_level == 'debug':
        return logging.DEBUG
    elif log_level == 'error':
        return logging.ERROR
    elif log_level == 'warning':
        return logging.WARNING
    elif log_level == 'critical':
        return logging.CRITICAL
    else:
        return logging.INFO


def logging_init():
    filename = http_conf.get('log', "log_path")
    max_bytes = int(http_conf.get('log', "log_max_MB")) * 1024 * 1024
    backup_count = int(http_conf.get('log', "log_backup_count"))

    handler = RotatingFileHandler(filename=filename, maxBytes=max_bytes, backupCount=backup_count)

    log_level = switch_log_level(http_conf.get('log', "log_level"))
    log_fmt = '%(asctime)s %(levelname)s-%(thread)d-%(module)s-%(funcName)s-%(lineno)d:%(message)s'
    date_fmt = '%Y-%m-%d %H:%M:%S'

    logging.basicConfig(level=log_level, format=log_fmt, datefmt=date_fmt, handlers=[handler])

