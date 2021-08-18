#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 翻译插件,调用百度云,使用注意空格,格式:翻译 ENG 测试
@Date     :2021/07/19 14:27:12
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.utils.baiduUtils import TranslateUtil
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('translation')
class Translation:
    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        if re.match('翻译 .*', chains.asDisplay()) != None:
            message_text = chains.asDisplay().strip()
            msgs = message_text.split(' ')
            keyword = ''
            to_language = ''
            if len(msgs) >= 3:
                to_language = msgs[1]
                if to_language in ['中文', '汉字', '汉语', 'CN', 'cn', 'zh', 'ZH']:
                    to_language = 'zh'
                elif to_language in ['英语', '英文', 'en', 'EN', 'ENG', 'eng', 'english', 'ENGLISH', 'us', 'US']:
                    to_language = 'en'
                elif to_language in ['日文', '日语', 'JP', 'jp']:
                    to_language = 'jp'
                # 语种列表详见https://fanyi-api.baidu.com/doc/21
                keyword = ' '.join(msgs[2:])
                print('trans:to %s,keyword= %s' % (to_language, keyword))
                msgReq = MsgReq()
                try:
                    tranUtil = TranslateUtil()
                    result = tranUtil.translate(
                        keyword=keyword, to=to_language)
                    msg = MessageChain([Plain(text="text : %s\n" % keyword),
                                        Plain(text='to : %s\n' % to_language),
                                        Plain(text='result : %s' % result)])
                    msgReq.sendGroupMessage(msg=msg, target=group, quote=quote)
                except:
                    msg = MessageChain([Plain(text="调用百度翻译失败")])
                    msgReq.sendGroupMessage(msg=msg, target=group)
