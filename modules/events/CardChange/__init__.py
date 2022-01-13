#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 群员昵称改变
@Date     :2022/01/13 09:06:54
@Author      :yuejieyao
@version      :1.0
'''

from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Plain, At
from ..miraiEvent import MiraiEventProcessor
from modules.message.messageChain import MessageChain


@MiraiEventProcessor.mirai_member_card_change_event_register('CardChange')
class CardChange:
    NAME = "群员昵称改变"
    DESCRIPTION = """由于群员改昵称服务器并不会广播,只有当改变昵称的群员发言后才会被客户端检测到"""

    def process(self, group: int, qq: int, name_old: str, name_new: str):
        msg = MessageChain([At(qq), Plain(f"哎唷,新昵称不错哟")])
        MMR().sendGroupMessage(msg=msg, target=group)
