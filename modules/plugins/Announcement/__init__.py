#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 通过与bot私聊公告触发,bot监听之后的一次回复作为公告内容,发送到bot所在的群
@Date     :2021/06/11 14:32:43
@Author      :yuejieyao
@version      :1.0
"""
import time

from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('Announcement')
class Announcement:
    NAME = "群发"
    DESCRIPTION = "发送公告触发"

    def process(self, chains: MessageChain, target: int, quote: int):
        if chains.asDisplay() != '公告':
            return
        msg_req = MsgReq()
        msg = MessageChain([Plain(text="请回复公告内容,或回复取消/算了/cancel来取消这次公告")])
        msg_req.sendFriendMessage(msg=msg, target=target, quote=quote)

        def _filter(_msg: MessageChain, _target: int):
            return True

        def _callback(_msg: MessageChain, _target: int):
            if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                return
            _msg_req = MsgReq()
            _msg = MessageChain([Plain(text="接收到公告内容,即将开始发送公告")])
            _msg_req.sendFriendMessage(msg=_msg, target=_target)
            time.sleep(1)
            groups = MiraiMemberRequests().getGroupList()
            _msg = MessageChain([Plain(text="检测到已加入的群%d个" % len(groups))])
            _msg_req.sendFriendMessage(msg=_msg, target=_target)
            time.sleep(1)
            for group in groups:
                _msg = MessageChain([Plain(text="正在发送公告 - 群号:%d" % group.id)])
                _msg_req.sendGroupMessage(_msg, group.id)
                _msg_req.sendFriendMessage(msg=_msg, target=_target)
                time.sleep(0.5)
            _msg = MessageChain([Plain(text="公告发送完毕")])
            _msg_req.sendFriendMessage(_msg, target=_target)

        MiraiMessageMonitorHandler().add(MiraiMessageMonitor(
            monitor_type='FriendMessage', target=target, call_filter=_filter, call_func=_callback))  # 添加一次性监听
