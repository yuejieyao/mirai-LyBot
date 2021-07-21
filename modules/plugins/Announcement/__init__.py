#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 通过与bot私聊公告触发,bot监听之后的一次回复作为公告内容,发送到bot所在的群
@Date     :2021/06/11 14:32:43
@Author      :yuejieyao
@version      :1.0
'''
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
import time


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('announcement')
class Announcement:
    def process(self, chains: MessageChain, target: int, quote: int):
        if chains.asDisplay() != '公告':
            return
        msgReq = MsgReq()
        msg = MessageChain([Plain(text="请回复公告内容,或回复取消/算了/cancel来取消这次公告")])
        msgReq.sendFriendMessage(msg=msg, target=target, quote=quote)

        def filter(_msg: MessageChain, _target: int):
            return True

        def callback(_msg: MessageChain, _target: int):
            if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                return

            msg = MessageChain([Plain(text="接收到公告内容,即将开始发送公告")])
            msgReq.sendFriendMessage(msg=msg, target=_target)
            time.sleep(1)
            groups = MiraiMemberRequests().getGroupList()
            msg = MessageChain([Plain(text="检测到已加入的群%d个" % len(groups))])
            msgReq.sendFriendMessage(msg=msg, target=_target)
            time.sleep(1)
            for group in groups:
                msg = MessageChain([Plain(text="正在发送公告 - 群号:%d" % group.id)])
                msgReq.sendGroupMessage(_msg, group.id)
                msgReq.sendFriendMessage(msg=msg, target=_target)
                time.sleep(0.5)
            msg = MessageChain([Plain(text="公告发送完毕")])
            msgReq.sendFriendMessage(msg, target=_target)

        MiraiMessageMonitorHandler().add(MiraiMessageMonitor(
            type='FriendMessage', target=target, filter=filter, call=callback))  # 添加一次性监听
