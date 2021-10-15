#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 查字典,需要安装playwright的chromium
@Date     :2021/09/03 10:39:55
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from .modules.utils import screenshot
import re
import os
import uuid


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('xhdict')
class XHDict:
    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        message_display = chains.asDisplay().lower()
        if re.match('字典 .*', message_display) != None or re.match('dict .*', message_display) != None:
            msgs = message_display.split(' ')
            if len(msgs) != 2:
                return
            char = msgs[1]
            if len(char) != 1:
                return
            url = f"https://www.zdic.net/hans/{char}"
            temp_path = os.path.join(os.path.dirname(__file__), 'cache')
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)
            path = os.path.join(temp_path, f'{uuid.uuid1()}.png')
            try:
                screenshot.getScreenshot(url=url, path=path)
                MMR().sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

            except Exception:
                MMR().sendGroupMessage(msg=MessageChain([Plain(text="查询字典失败")]), target=group, quote=quote)
