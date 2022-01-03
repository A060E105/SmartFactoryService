#!/usr/bin/python3

import logging
from logging.handlers import RotatingFileHandler
import sty

log = logging.getLogger('dev')
log.setLevel(logging.INFO)

date_format = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(f'{sty.fg(96, 96, 96)}%(asctime)s->%(filename)s:%(levelname)s: %(message)s{sty.fg.rs}',
                              datefmt=date_format)
file_format = logging.Formatter('%(asctime)s->%(filename)s:%(levelname)s: %(message)s', datefmt=date_format)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

rotating_handler = RotatingFileHandler('SmartFactory.log', maxBytes=20000, backupCount=1)
rotating_handler.setFormatter(file_format)

log.addHandler(handler)
log.addHandler(rotating_handler)


def get_logger():
    return log


if __name__ == '__main__':
    log.info('Start precess')

    log.debug(f'This is debug')
    log.error('This is error')
    try:
        raise Exception('catch exception')
    except Exception:
        log.exception('get exception')

    log.info('End precess')

# ==============================================================================
# ------------------------------------ END -------------------------------------
# ==============================================================================
