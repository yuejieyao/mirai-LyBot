#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 此代码目的是持久化提醒功能,避免bot在重启后丢失之前尚未提醒的记录
@Date     :2021/12/23 10:20:29
@Author      :yuejieyao
@version      :1.0
"""
import traceback
from datetime import datetime

from modules.dataSource.scheduleDataSource import DataSource
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, At
from modules.utils import log
from ..miraiSchedule import MiraiScheduleProcessor

log.info('checking remind not send...')
schedule_db = 'modules/resource/data/schedule.db'
try:
    ds = DataSource(schedule_db)
    reminds = ds.get_remind_less_than_now()
    if len(reminds):
        log.info(f'find {len(reminds)} remind not send')
    for r in reminds:
        _id, date, content, target, group = r[0], datetime.strptime(
            r[1], "%Y-%m-%d %H:%M:%S"), str(r[2]), int(r[3]), int(r[4])


        def do_job():
            MiraiMessageRequest().sendGroupMessage(msg=MessageChain([At(target=target), Plain(text=content)]),
                                                   target=group)
            DataSource(schedule_db).set_send(id=_id)


        MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(run_date=date, func=do_job)
        log.info(f"[Schedule][Remind] add remind in {datetime.strftime(date, '%Y-%m-%d %H:%M:%S')}")

except:
    log.error(traceback.format_exc())
