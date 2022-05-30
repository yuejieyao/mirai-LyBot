import os
import time

LOG_PATH = 'modules/resource/log'


def get_log_path():
    name = time.strftime('%Y%m%d', time.localtime()) + '.log'
    return os.path.join(LOG_PATH, name)


def mprint(print_type: str, msg: str, log: bool):
    """[TIME][TYPE] msg"""
    prefix = '[%s][%s] ' % (time.strftime('%H:%M:%S', time.localtime()), print_type.upper())
    if '\n' in msg:
        msg = msg.replace('\n', '\n' + ' ' * len(prefix))
    text = prefix + msg

    print(text)

    if log:
        mlog(text)


def info(msg: str, log: bool = False):
    mprint(print_type='INFO', msg=msg, log=log)


def error(msg: str, log: bool = True):
    mprint(print_type='ERROR', msg=msg, log=log)


def mlog(msg: str):
    try:
        with open(file=get_log_path(), encoding='utf-8', mode='a+') as fs:
            fs.write(msg + '\n')
    except Exception as e:
        print(e)
