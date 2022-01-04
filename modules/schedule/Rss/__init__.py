#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: RSS订阅轮训任务
@Date     :2021/08/27 10:53:54
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiSchedule import MiraiScheduleProcessor
from modules.plugins.Rss.modules.utils.dataSource import DataSource
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.utils import log as Log
import traceback
import time


@MiraiScheduleProcessor.mirai_schedule_plugin_every_minute_register(interval=10)
class Rss:
    rss_db = 'modules/resource/data/rss.db'

    def process(self):
        ds = DataSource(path=self.rss_db)
        # 获取订阅的urls
        urls = ds.getSubUrls()
        for url in urls:
            try:
                Log.info(f'[Schedule][RSS] check rss url={url}')
                # 获取rss消息并生成MessageChain
                rsses = ds.getMultNew(url=url)
                for rss in rsses:
                    msg = MessageChain([])
                    # 屏蔽中奖动态
                    if '中奖' in rss['title'] or '中奖' in rss['description']:
                        continue

                    # 防止标题和内容重复
                    if rss['title'] not in rss['description']:
                        msg.append(Plain(text=rss['title']+'\n'))
                    msg.append(Plain(text=rss['description']+'\n'))
                    for img_url in rss['img'].split(','):
                        if img_url:
                            img = Image(image_type='group', image_url=img_url)
                            if img.image_id:
                                msg.append(img)
                    msg.append(Plain(text=rss['link']))
                    # 获取订阅该url的所有群号
                    groups = ds.getFollowers(url=url)
                    for group in groups:
                        # 判断是否发送过
                        if not ds.isSend(rss_id=rss['rss_id'], group=group):
                            MMR().sendGroupMessage(msg=msg, target=group)
                            ds.setSend(rss_id=rss['rss_id'], group=group)
                    time.sleep(10)
            except Exception:
                Log.error(msg=traceback.format_exc())
