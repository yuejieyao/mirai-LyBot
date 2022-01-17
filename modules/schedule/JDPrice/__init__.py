#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: JD价格监控轮询插件
@Date     :2022/01/14 15:20:57
@Author      :yuejieyao
@version      :1.0
'''
from importlib.resources import path
from ..miraiSchedule import MiraiScheduleProcessor
from modules.plugins.JDPrice.modules.utils.dataSource import DataSource
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image, At
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.dataSource.miraiDataSource import MiraiDataSource as MD
from modules.utils import log as Log
import traceback


@MiraiScheduleProcessor.mirai_schedule_plugin_every_hour_register(schedule_name='JDPriceSchedule', interval=1)
class JDPriceSchedule:
    NAME = "JD价格监控轮询插件"
    DESCRIPTION = "主动推送关注商品的价格变动"

    jd_db = 'modules/resource/data/jd.db'

    def process(self):
        try:
            ds = DataSource(path=self.jd_db)
            goods_ids = ds.getFollowedGoods()
            for goods_id in goods_ids:
                Log.info(msg=f'[Schedule][JDPrice] check jd price by goods_id = {goods_id}')
                if ds.isPriceChange(goods_id):
                    Log.info(msg=f'[Schedule][JDPrice] [{goods_id}(Goods_ID)] Price Changed')
                    url, path = ds.create_current_img(goods_id)
                    followers = ds.getFollowedUsers(goods_id)
                    groups = list(set(follower[0] for follower in followers))
                    for group in groups:
                        if MD().isScheduleClose(register_name='JDPriceSchedule', group=group):
                            continue
                        qqs = list(set([follower[1] for follower in followers if follower[0] == group]))
                        msg = MessageChain([])
                        for qq in qqs:
                            msg.append(At(target=qq))
                        msg.extend([Plain(text=f" 购物车中商品价格或优惠信息发生了变动~\n商品链接:{url}\n"), Image(
                            image_type='group', file_path=path)])
                        MMR().sendGroupMessage(msg=msg, target=group)

        except:
            Log.error(msg=traceback.format_exc())
