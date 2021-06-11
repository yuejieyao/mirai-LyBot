# encoding utf-8
# name:config.py

import configparser


class config(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr: str) -> str:
      # 去掉大小写转换
        return optionstr
        # return super().optionxform(optionstr)


def getMiraiConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='mirai', option=option)
    else:
        return conf['mirai']


def setMiraiConf(option: str, value: str):
    conf = config()
    conf.read('bot.conf')
    conf.set(section='mirai', option=option, value=value)

    with open('bot.conf', 'w+') as f:
        conf.write(f)


def getBaiduConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='baidu', option=option)
    else:
        return conf['baidu']
