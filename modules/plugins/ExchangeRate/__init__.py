#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 汇率转换,调用格式:rate 1000 jpy cny
@Date     :2021/07/20 12:43:08
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.conf import config
import re
import requests


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('exchangeRate')
class ExchangeRate:
    def process(self, chains: MessageChain, group: int, quote: int):
        if re.match('rate .*', chains.asDisplay()) != None:
            msgs = chains.asDisplay().split(' ')
            msgReq = MiraiMessageRequest()
            if len(msgs) == 4:
                from_num = float(msgs[1])
                from_country = msgs[2]
                to_country = msgs[3]
                if from_num > 0:
                    print(
                        f'exchange rate: {from_num} {from_country} to {to_country}')
                    msgReq.sendGroupMessage(msg=get_exchange_rate(
                        from_num=from_num, from_country=from_country, to_country=to_country), target=group, quote=quote)
                else:
                    msgReq.sendGroupMessage(msg=MessageChain(
                        [Plain(text="不支持的格式,示例:\nrate 10000 jpy cny")]), target=group, quote=quote)
            else:
                msgReq.sendGroupMessage(msg=MessageChain(
                    [Plain(text="不支持的格式,示例:\nrate 10000 jpy cny")]), target=group, quote=quote)


def get_exchange_rate(from_num: float, from_country: str, to_country: str) -> MessageChain:
    conf = config.getFixerConf()
    token = conf['token']
    rate_url = f'http://data.fixer.io/api/latest?access_key={token}&format=1'
    try:
        msg = None
        resp = requests.session().get(url=rate_url)
        if resp.status_code == 200:
            result = resp.json()
            if 'success' in result:
                from_country = from_country.upper()
                to_country = to_country.upper()
                rates = result['rates']
                if from_country in rates and to_country in rates:
                    to_num = from_num/rates[from_country]*rates[to_country]
                    msg = MessageChain([
                        Plain(text='转换结果: %.4f %s' % (to_num, to_country))
                    ])
                else:
                    msg = MessageChain([
                        Plain(
                            text='仅支持3位简写,忽略大小写,常用(CNY,JPY,USD,TWD,EUR,INR,GBP等)')
                    ])
            else:
                msg = MessageChain([Plain(text='fixer调用失败')])
            return msg

    except:
        msg = MessageChain([Plain(text='fixer调用失败')])
        return msg
