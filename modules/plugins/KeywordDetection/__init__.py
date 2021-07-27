#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 对消息文本和图片进行关键词匹配,匹配成功则触发撤回,需要管理员权限,非群主无法撤回管理员消息
@Date     :2021/06/10 11:25:20
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.utils.baiduUtils import OcrUtil
import time
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('keywordDetection')
class KeywordDetection:
    def process(self, chains: MessageChain, group: int, quote: int):
        taboos = ['微博']
        for taboo in taboos:
            # 检测文本中包含关键词
            if re.match(f'.*{taboo}.*', chains.asDisplay()) != None:
                msgReq = MsgReq()
                try:
                    msgReq.recall(target=quote)
                except:
                    msg = MessageChain(
                        [Plain('检测到关键词[%s],但我没有权限撤回你,算你牛逼' % taboo)])
                    msgReq.sendGroupMessage(msg=msg, target=group, quote=quote)
                else:
                    msg = MessageChain([Plain('检测到关键词[%s],自动撤回' % taboo)])
                    msgReq.sendGroupMessage(msg=msg, target=group)

            # 检测图片中包含关键词
            images = chains.get(Image)
            if len(images) > 0:
                ocrUtil = OcrUtil()
                for img in images:
                    url = img.chain['url']
                    charlist = ocrUtil.basicGeneralUrl(url)
                    if len(charlist) > 0:
                        if re.match(f'.*{taboo}.*', ' '.join(charlist)) != None:
                            msgReq = MsgReq()
                            try:
                                msgReq.recall(target=quote)
                            except:
                                msg = MessageChain(
                                    [Plain('检测到关键词[%s],但我没有权限撤回你,算你牛逼' % taboo)])
                                msgReq.sendGroupMessage(
                                    msg=msg, target=group, quote=quote)
                            else:
                                msg = MessageChain(
                                    [Plain('检测到关键词[%s],自动撤回' % taboo)])
                                msgReq.sendGroupMessage(
                                    msg=msg, target=group)
                            break
                    time.sleep(0.5)
