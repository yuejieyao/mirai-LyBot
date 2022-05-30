#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 设置一次性提醒功能,格式:提醒我 下午两点 午休结束
@Date     :2021/09/15 15:34:13
@Author      :yuejieyao
@version      :1.0
"""

import re
import traceback
from datetime import datetime

from pyunit_time import Time

from modules.dataSource.scheduleDataSource import DataSource
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import At, Plain
from modules.schedule.miraiSchedule import MiraiScheduleProcessor
from modules.utils import log
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Remind')
class Remind:
    schedule_db = 'modules/resource/data/schedule.db'

    NAME = "提醒"
    DESCRIPTION = """设置一次性提醒发送:提醒我 时间字符串 提醒内容
    如:提醒我 下午2点 上班,提醒我 明天早上6点半 上班,提醒我 今晚7点 健身环"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay()
        if re.match('提醒我 .*', msg_display) is None:
            return

        msgs = msg_display.split(' ')
        if len(msgs) != 3:
            return
        t = Time(datetime.now().strftime('%Y-%m-%d') + ' 00:00:00').parse(msgs[1])
        t = t[0] if len(t) > 0 else None
        if not t:
            MiraiMessageRequest().sendGroupMessage(MessageChain(
                [Plain(text='无法解析时间字符串,请使用如下格式:提醒我 下午2点 上班')]), target=group, quote=quote)
            return
        try:

            ds = DataSource(self.schedule_db)
            _id = ds.add_timing_remind(date=t['keyDate'], content=msgs[2], target=target, group=group)

            def remind():
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain([At(target=target), Plain(text=msgs[2])]),
                                                       target=group)
                ds.set_send(_id)

            MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                run_date=datetime.strptime(t['keyDate'], '%Y-%m-%d %H:%M:%S'), func=remind)

            MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                [Plain(text=f"成功添加提醒,将在{t['keyDate']}触发")]), target=group, quote=quote)
        except:
            log.error(traceback.format_exc())
