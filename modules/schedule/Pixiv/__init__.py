#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: P站关注循环任务(关注并没有真的在P站帐号上关注)
@Date     :2021/08/17 15:45:26
@Author      :yuejieyao
@version      :1.0
'''
from ..miraiSchedule import MiraiScheduleProcessor
from modules.plugins.Pixiv.modules.utils.dataSource import DataSource
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image, At
from modules.http.miraiMessageRequest import MiraiMessageRequest
import time
import shutil
import os


@MiraiScheduleProcessor.mirai_schedule_plugin_every_hour_register(interval=1)
class Pixiv:
    pixiv_db = 'modules/resource/data/pixiv.db'

    def process(self):
        ds = DataSource(path=self.pixiv_db)
        # 获取被关注的作者Ids
        author_ids = ds.getFollowAuthorIds()
        for author_id in author_ids:
            # 避免过快访问P站被ban,每次获取间隔5秒
            time.sleep(5)
            try:
                print(f'schedule: 开始检测Pixiv作者ID:{author_id}的新作品')
                # 获取最后更新的图,检查是否推送过
                pic = ds.getNewPic(user=author_id)
                followers = ds.getFollowers(user=author_id)
                # 需要发送的群
                groups = list(set(follower[0] for follower in followers))
                for group in groups:
                    if ds.isSend(id=pic['id'], group=group):
                        continue
                    # 该群需要@的人员
                    qqs = list(set([follower[1] for follower in followers if follower[0] == group]))
                    msg = MessageChain([])
                    for qq in qqs:
                        msg.append(At(target=qq))
                    msg.extend([Plain(text="新图推送~\n"),
                                Plain(text=f"title : {pic['title']}\n"),
                                Plain(text=f"author : {pic['author']}({pic['user']})\n"),
                                Plain(text=f"tags : {pic['tag']}\n"),
                                Image(image_type='group', file_path=pic['path'])])
                    MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
                    time.sleep(1)
                    # 推送完成后更改图片已推送
                    ds.setSend(id=pic['id'], group=group)
            except Exception as e:
                print(e)


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(days=1, time="04:00")
class PixivDayly:
    pixiv_db = 'modules/resource/data/pixiv.db'

    def process(self):
        ds = DataSource(path=self.pixiv_db)
        try:
            if ds.initRankingPic():
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据成功")]))
            else:
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据失败")]))
        except Exception as e:
            print(e)
            MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据失败")]))


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(days=1, time="04:00")
class PixivCacheDelete:
    directory = "modules/resource/illusts"

    def process(self):
        # 删除缓存图片
        shutil.rmtree(path=self.directory)
        os.mkdir(path=self.directory)
