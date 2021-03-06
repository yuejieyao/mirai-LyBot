#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 汇率转换,调用格式:rate 1000 jpy cny
@Date     :2021/07/20 12:43:08
@Author      :yuejieyao
@version      :1.0
"""
import re
import traceback

import jieba
import requests

from modules.conf import config
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from modules.utils import log, common
from ..miraiPlugin import MiraiMessagePluginProcessor

jieba.load_userdict('modules/plugins/ExchangeRate/resource/userdict.txt')


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('ExchangeRate')
class ExchangeRate:
    NAME = "汇率转换"
    DESCRIPTION = """发送如:100块钱等于多少日元,300港币是多少钱,包含需要查询的关键词即可
    """

    currency = {
        'CNY': ['CNY', '人民币', '块钱'],
        'JPY': ['JPY', '日元'],
        'HKD': ['HKD', '港元', '港币'],
        'TWD': ['TWD', '台币', '新台币'],
        'USD': ['USD', '美刀', '美元', '刀'],
        'EUR': ['EUR', '欧元'],
        'INR': ['INR', '印度卢比', '卢比', '印度币'],
        'GBP': ['GBP', '英镑'],
        'DEM': ['DEM', '德国马克', '马克', '德币'],
        'CHF': ['CHF', '瑞士法郎', '瑞士币'],
        'FRF': ['FRF', '法国法郎', '法郎', '法国币'],
        'NLG': ['NLG', '荷兰盾', '盾', '荷兰币'],
        'ITL': ['ITL', '意大利里拉', '里拉', '意大利币'],
        'KRW': ['KRW', '韩国圆', '韩币', '韩元'],
        'THB': ['THB', '泰铢', '泰国铢', '泰币'],
        'SGD': ['SGD', '新加坡元', '新加坡币'],
        'AUD': ['AUD', '澳元'],
        'MOP': ['MOP', '澳门币'],
        'VND': ['VND', '越南盾', '越南币'],
        'ARS': ['ARS', '阿根廷比索', '比索', '阿根廷币'],
        'TRY': ['TRY', '土耳其里拉', '土耳其币'],
        'NZD': ['NZD', '纽西兰刀']
    }

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay().upper()
        if re.match('(汇率|rate).*', msg_display) or re.match('\\d+\\s*', msg_display):
            try:
                # 获取消息中的第一个数值,作为金额,若没有就取100
                find_amount = list(filter(None, re.findall("\\d*", msg_display)))
                amount = int(find_amount[0]) if len(find_amount) else 100

                # 分词后与关键词列表取交集
                keywords_all = [s for key in self.currency for s in self.currency[key]]
                seg_list = jieba.lcut(msg_display, cut_all=False)
                find_currencys = [i for i in seg_list if i in keywords_all]

                if len(find_currencys) == 2:
                    from_country = self.getCurrency(find_currencys[0])
                    to_country = self.getCurrency(find_currencys[1])
                    if from_country and to_country:
                        log.info(msg=f'[Plugin][ExchangeRate] {amount} {from_country} to {to_country}')
                        msg = get_exchange_rate(amount, from_country, to_country)
                        if msg:
                            MiraiMessageRequest().sendGroupMessage(msg=msg, target=group, quote=quote)
                elif len(find_currencys) == 1:
                    from_country = self.getCurrency(find_currencys[0])
                    # 1000日元值多少,1000日元
                    if from_country != 'CNY':
                        to_country = 'CNY'
                        log.info(msg=f'[Plugin][ExchangeRate] {amount} {from_country} to {to_country}')
                        MiraiMessageRequest().sendGroupMessage(msg=get_exchange_rate(amount, from_country, to_country),
                                                               target=group, quote=quote)
            except:
                log.error(traceback.format_exc())
        elif msg_display == "常用货币":
            try:
                strs = '\n'.join([f"\"{key}\": {','.join(self.currency[key])}" for key in self.currency])
                path = common.text_to_img(strs)
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Image(image_type='group', file_path=path)]),
                                                       target=group)
            except:
                log.error(traceback.format_exc())

    def getCurrency(self, keyword: str) -> str:
        for key in self.currency:
            if keyword in self.currency[key]:
                return key
        return ''


def get_exchange_rate(from_num: int, from_country: str, to_country: str) -> MessageChain:
    token = config.getConf('fixer', 'token')
    rate_url = f'http://data.fixer.io/api/latest?access_key={token}&format=1'
    resp = requests.session().get(url=rate_url)
    if resp.status_code == 200:
        result = resp.json()
        if 'success' in result:
            from_country = from_country.upper()
            to_country = to_country.upper()
            rates = result['rates']
            if from_country in rates and to_country in rates:
                to_num = from_num / rates[from_country] * rates[to_country]
                return MessageChain([
                    Plain(text='%.4f %s价值%.4f %s' % (from_num, from_country, to_num, to_country))
                ])
            else:
                log.error("[Plugins][ExchangeRate]" + resp.text)
        else:
            log.error("[Plugins][ExchangeRate]" + resp.text)
    return MessageChain([Plain(text='转换失败')])
