#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 订阅rss
@Date     :2021/08/27 09:15:09
@Author      :yuejieyao
@version      :1.0
"""
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageType import Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.dataSource import DataSource
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Rss')
class Rss:
    NAME = "RssHub订阅"
    DESCRIPTION = """仅支持管理员自建Rsshub
    订阅:订阅rss url地址
    取消订阅:取消订阅rss"""

    rss_db = 'modules/resource/data/rss.db'

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay().lower()
        if re.match('订阅rss .*', msg_display) is not None:
            ds = DataSource(path=self.rss_db)
            msgs = msg_display.split(' ')
            if len(msgs) == 2:
                url = msgs[1]
                if ds.sub(url=url, group=group):
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="订阅成功")]), target=group,
                                                           quote=quote)
                else:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="订阅失败")]), target=group,
                                                           quote=quote)

        elif re.match('取消订阅rss.*', msg_display) is not None:
            ds = DataSource(path=self.rss_db)
            rs = ds.showSub(group=group)
            if len(rs) == 0:
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="未找到任何订阅信息")]), target=group,
                                                       quote=quote)
                return
            msg = MessageChain([Plain(text="当前订阅信息如下,请回复需要取消订阅的ID号\n")])
            for r in rs:
                msg.append(Plain(text=f"ID: {r[0]} , Title: {r[1]}"))
            MiraiMessageRequest().sendGroupMessage(msg=msg, target=group, quote=quote)

            def _filter(_msg: MessageChain, _target: int, _group: int):
                if _target == target and _group == group:
                    _msg_asdisplay = _msg.asDisplay()
                    if _msg_asdisplay.isdigit() and int(_msg_asdisplay) in [_r[0] for _r in rs]:
                        return True
                    elif _msg_asdisplay in ('取消', '算了', 'cancel'):
                        return True
                return False

            def _callback(_msg: MessageChain, _target: int, _group: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                else:
                    _id = int(_msg.asDisplay())
                    if ds.unSub(_id=_id):
                        MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="取消订阅成功")]), target=_group)
                    else:
                        MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="取消订阅失败")]), target=_group)

            MiraiMessageMonitorHandler().add(
                MiraiMessageMonitor(monitor_type='GroupMessage', target=target, call_filter=_filter,
                                    call_func=_callback))  # 添加一次性监听
