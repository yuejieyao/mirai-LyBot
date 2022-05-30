#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 群成员禁言事件
@Date     :2022/01/12 14:36:55
@Author      :yuejieyao
@version      :1.0
"""
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, At
from ..miraiEvent import MiraiEventProcessor


@MiraiEventProcessor.mirai_member_mute_event_register('MemberMute')
class MemberMute:
    NAME = "群成员禁言事件"
    DESCRIPTION = """围观"""

    def process(self, group: int, qq: int, operator: int, seconed: int):
        msg = MessageChain([Plain(text="咦?"), At(target=qq), Plain(text="被"),
                           At(target=operator), Plain(text=f"禁言了{seconed}秒,是怎么回事呢?")])
        MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
