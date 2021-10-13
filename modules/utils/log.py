import os
import time
LOG_PATH = 'modules/utils/log'


def get_log_path(self):
    name = time.strftime('%Y%m%d', time.localtime()) + '.log'
    return os.path.join(LOG_PATH, name)


def mprint(type: str, msg: str, log: bool):
    """[TIME][TYPE] msg"""
    prefix = '[%s][%s] ' % (time.strftime('%H:%M:%S', time.localtime()), type.upper())
    if '\n' in msg:
        msg = msg.replace('\n', '\n'+' '*len(prefix))
    text = prefix+msg

    print(text)

    if log:
        log(text)


def info(msg: str, log: bool = False):
    mprint(type='INFO', msg=msg, log=log)


def error(msg: str, log: bool = True):
    mprint(type='ERROR', msg=msg, log=log)


def log(msg: str):
    try:
        with open(file=get_log_path(), encoding='utf-8', mode='a+') as fs:
            fs.write(msg+'\n')
    except Exception:
        pass
