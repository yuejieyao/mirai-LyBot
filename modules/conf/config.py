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


def getConf(section: str, option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section=section, option=option)
    else:
        return conf[section]


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


def getBaiduOcrConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='baidu_ocr', option=option)
    else:
        return conf['baidu_ocr']


def getBaiduTranConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='baidu_translate', option=option)
    else:
        return conf['baidu_translate']


def getFixerConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='fixer', option=option)
    else:
        return conf['fixer']


def getLoliconConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='lolicon', option=option)
    else:
        return conf['lolicon']


def getQWeatherConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='qweather', option=option)
    else:
        return conf['qweather']


def getPixivConf(option: str = None):
    conf = config()
    conf.read('bot.conf')
    if option:
        return conf.get(section='pixiv', option=option)
    else:
        return conf['pixiv']
