#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 获取bot当前IP
@Date     :2021/08/18 14:38:14
@Author      :yuejieyao
@version      :1.0
"""
import requests

from modules.conf import config
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('MyIP')
class MyIP:
    NAME = "我的IP"
    DESCRIPTION = "返回服务器当前IP地址"

    def process(self, chains: MessageChain, target: int, quote: int):
        if str(target) == config.getConf('mirai', 'adminQQ'):
            if chains.asDisplay() == "myip":
                resp = requests.session().get(url="http://myip.ipip.net/")
                resp.raise_for_status()
                result = resp.content.decode('utf-8')
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text=result)]))
