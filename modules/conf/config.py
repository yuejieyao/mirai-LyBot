# encoding utf-8
# name:config.py

import configparser


class Config(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr: str) -> str:
        # 去掉大小写转换
        return optionstr
        # return super().optionxform(optionstr)


def getConf(section: str, option: str = None):
    conf = Config()
    conf.read('bot.conf')
    if option:
        return conf.get(section=section, option=option)
    else:
        return conf[section]


def setConf(section: str, option: str, value: str):
    conf = Config()
    conf.read('bot.conf')
    conf.set(section=section, option=option, value=value)

    with open('bot.conf', 'w+') as f:
        conf.write(f)
