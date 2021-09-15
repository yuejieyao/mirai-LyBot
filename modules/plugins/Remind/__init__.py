#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 设置一次性提醒功能,格式:提醒我 下午两点 午休结束
@Date     :2021/09/15 15:34:13
@Author      :yuejieyao
@version      :1.0
'''

from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import At, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.schedule.miraiSchedule import MiraiScheduleProcessor
from pyunit_time import Time
from datetime import datetime
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('remind')
class Remind:
    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        msg_display = chains.asDisplay()
        if re.match('提醒我 .*', msg_display) == None:
            return

        msgs = msg_display.split(' ')
        if len(msgs) != 3:
            return
        t = Time(datetime.now().strftime('%Y-%m-%d')+' 00:00:00').parse(msgs[1])
        t = t[0] if len(t) > 0 else None
        if not t:
            MMR().sendGroupMessage(MessageChain(
                [Plain(text='无法解析时间字符串,请使用如下格式:提醒我 下午2点 上班')]), target=group, quote=quote)
            return

        def remind():
            MMR().sendGroupMessage(msg=MessageChain([At(target=target), Plain(text=msgs[2])]), target=group)

        MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
            run_date=datetime.strptime(t['keyDate'], '%Y-%m-%d %H:%M:%S'), func=remind)

        MMR().sendGroupMessage(msg=MessageChain([Plain(text=f"成功添加提醒,将在{t['keyDate']}触发")]), target=group, quote=quote)
