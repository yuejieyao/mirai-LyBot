#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 翻译插件,调用百度云,使用注意空格,格式:翻译 ENG 测试
@Date     :2021/07/19 14:27:12
@Author      :yuejieyao
@version      :1.0
"""

import re

from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.utils.baiduUtils import TranslateUtil
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Translation')
class Translation:
    NAME = "翻译"
    DESCRIPTION = """发送:翻译 目标语种 翻译内容
    目标语种为简写,如EN,JP,CN(ZH)等,详见https://fanyi-api.baidu.com/doc/21"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        if re.match('翻译 .*', chains.asDisplay()) is not None:
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
                msg_req = MsgReq()
                try:
                    tran_util = TranslateUtil()
                    result = tran_util.translate(
                        keyword=keyword, to=to_language)
                    msg = MessageChain([Plain(text="text : %s\n" % keyword),
                                        Plain(text='to : %s\n' % to_language),
                                        Plain(text='result : %s' % result)])
                    msg_req.sendGroupMessage(msg=msg, target=group, quote=quote)
                except:
                    msg = MessageChain([Plain(text="调用百度翻译失败")])
                    msg_req.sendGroupMessage(msg=msg, target=group)
