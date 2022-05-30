#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 欢迎入群
@Date     :2022/01/11 10:57:44
@Author      :yuejieyao
@version      :1.0
"""
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.message.messageType import Plain, At
from ..miraiEvent import MiraiEventProcessor
from modules.message.messageChain import MessageChain


@MiraiEventProcessor.mirai_join_event_register('Welcome')
class Welcome:
    NAME = "新进人员欢迎"
    DESCRIPTION = """欢迎入群"""

    def process(self, group: int, qq: int, name: str):
        bot_info = MiraiMemberRequests().getBotInfo()
        MiraiMessageRequest().sendGroupMessage(msg=MessageChain([At(target=qq), Plain(
            text=f"欢迎{name},我是{bot_info.nickname},请多多指教哦~")]), target=group)
