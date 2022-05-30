#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: RSS订阅轮训任务
@Date     :2021/08/27 10:53:54
@Author      :yuejieyao
@version      :1.0
"""

import time
import traceback

from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.plugins.Rss.modules.utils.dataSource import DataSource
from modules.utils import log
from ..miraiSchedule import MiraiScheduleProcessor


@MiraiScheduleProcessor.mirai_schedule_plugin_every_minute_register(schedule_name='RssSchedule', interval=10)
class RssSchedule:
    NAME = "RSS推送服务"
    DESCRIPTION = "主动推送已订阅的rss更新"

    rss_db = 'modules/resource/data/rss.db'

    def process(self):
        ds = DataSource(path=self.rss_db)
        # 获取订阅的urls
        urls = ds.getSubUrls()
        for url in urls:
            try:
                log.info(f'[Schedule][RSS] check rss url={url}')
                # 获取rss消息并生成MessageChain
                rsses = ds.getMultNew(url=url)
                # 如果一下获取到很多(10条),就当成是首次订阅的情况,只发一条
                groups = ds.getFollowers(url=url)
                if len(rsses) > 9:
                    for rss in rsses[1:10]:
                        for group in groups:
                            ds.setSend(rss_id=rss['rss_id'], group=group)
                for rss in rsses:
                    for group in groups:
                        if MiraiDataSource().isScheduleClose(register_name='RssSchedule', group=group):
                            continue
                        # 判断是否发送过
                        if not ds.isSend(rss_id=rss['rss_id'], group=group):
                            msg = MessageChain([])
                            # 屏蔽中奖动态
                            if '中奖' in rss['title'] or '中奖' in rss['description']:
                                continue

                            # 防止标题和内容重复
                            if rss['title'] not in rss['description']:
                                msg.append(Plain(text=rss['title'] + '\n'))
                            msg.append(Plain(text=rss['description'] + '\n'))
                            for img_url in rss['img'].split(','):
                                if img_url:
                                    img = Image(image_type='group', image_url=img_url)
                                    if img.image_id:
                                        msg.append(img)
                            msg.append(Plain(text=rss['link']))
                            # 获取订阅该url的所有群号
                            MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
                            ds.setSend(rss_id=rss['rss_id'], group=group)
                    time.sleep(10)
            except:
                log.error(msg=traceback.format_exc())
