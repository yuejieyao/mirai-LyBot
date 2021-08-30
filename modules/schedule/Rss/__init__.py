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



@MiraiScheduleProcessor.mirai_schedule_plugin_every_minute_register(interval=10)
class Rss:
    rss_db = 'modules/resource/data/rss.db'

    def process(self):
        ds = DataSource(path=self.rss_db)
        # 获取订阅的urls
        urls = ds.getSubUrls()
        for url in urls:
            try:
                # 获取rss消息并生成MessageChain
                rss = ds.getNew(url=url)
                msg = MessageChain([])
                # 防止标题和内容重复
                if rss['title'] not in rss['description']:
                    msg.append(Plain(text=rss['title']+'\n'))
                msg.append(Plain(text=rss['description']+'\n'))
                for img_url in rss['img'].split(','):
                    msg.append(Image(image_type='group', image_url=img_url))
                msg.append(Plain(text=rss['link']))
                # 获取订阅该url的所有群号
                groups = ds.getFollowers(url=url)
                for group in groups:
                    # 判断是否发送过
                    if not ds.isSend(rss_id=rss['rss_id'], group=group):
                        MMR().sendGroupMessage(msg=msg, target=group)
                        ds.setSend(rss_id=rss['rss_id'], group=group)

            except Exception as e:
                print(e)
