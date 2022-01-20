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
from modules.dataSource.miraiDataSource import MiraiDataSource as MD
from modules.utils import log as Log
import time
import shutil
import uuid
import os
import traceback


@MiraiScheduleProcessor.mirai_schedule_plugin_every_hour_register(schedule_name='PixivSchedule', interval=1)
class PixivSchedule:
    NAME = "P站关注推送服务"
    DESCRIPTION = "主动推送已关注作者的新图"

    pixiv_db = 'modules/resource/data/pixiv.db'
    directory = "modules/resource/illusts"

    def process(self):
        ds = DataSource(path=self.pixiv_db)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        # 获取被关注的作者Ids
        author_ids = ds.getFollowAuthorIds()
        for author_id in author_ids:
            # 避免过快访问P站被ban,每次获取间隔10秒
            time.sleep(10)
            try:
                Log.info(msg=f'[Schedule][Pixiv] check new works by author_id = {author_id}')
                # 获取最后更新的图,检查是否推送过
                pic = ds.getNewPic(user=author_id)
                followers = ds.getFollowers(user=author_id)
                # 需要发送的群
                groups = list(set(follower[0] for follower in followers))
                # 下载图片文件名
                fname = f"{uuid.uuid1()}.png"
                path = os.path.join(self.directory, fname)

                for group in groups:
                    if MD().isScheduleClose(register_name='PixivSchedule', group=group):
                        continue
                    if ds.isSend(id=pic['id'], group=group):
                        continue
                    # 在有需要发送的群的前提下,下载图片
                    if not os.path.exists(path=path):
                        if ds.pixiv.downImg(url=pic['url'], path=self.directory, name=fname):
                            Log.info(f"[Plugins][Pixiv] download IMG[{pic['id']}(ID)][{path}(Path)] success")
                    # 该群需要@的人员
                    qqs = list(set([follower[1] for follower in followers if follower[0] == group]))
                    msg = MessageChain([])
                    for qq in qqs:
                        msg.append(At(target=qq))
                    msg.extend([Plain(text=" 新图推送~\n"),
                                Plain(text=f"title : {pic['title']}\n"),
                                Plain(text=f"author : {pic['author']}({pic['user']})\n"),
                                Plain(text=f"tags : {pic['tag']}\n")])
                    img=Image(image_type='group', file_path=path)
                    # 图片过大返回false,不推送但也set成已推送
                    if img.image_id:
                        msg.append(img)
                        MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
                    time.sleep(1)
                    # 推送完成后更改图片已推送
                    ds.setSend(id=pic['id'], group=group)
            except Exception:
                Log.error(msg=traceback.format_exc())


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('PixivDayly', 4, 1)
class PixivDayly:
    NAME = "P站榜单数据更新"
    DESCRIPTION = "每日4点更新P站榜单数据"
    pixiv_db = 'modules/resource/data/pixiv.db'

    def process(self):
        ds = DataSource(path=self.pixiv_db)
        try:
            if ds.initRankingPic():
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据成功")]))
            else:
                MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据失败")]))
        except Exception:
            Log.error(msg=traceback.format_exc())
            MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="更新日榜单数据失败")]))
        else:
            ds.close()


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('PixivCacheDelete', 4, 10)
class PixivCacheDelete:
    NAME = "P站缓存清理"
    DESCRIPTION = "每日4点清理P站缓存"
    directory = "modules/resource/illusts"

    def process(self):
        try:
            # 删除缓存图片
            shutil.rmtree(path=self.directory)
            os.mkdir(path=self.directory)
            MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="Pixiv:删除缓存图片成功")]))
        except Exception:
            Log.error(msg=traceback.format_exc())
            MiraiMessageRequest().sendAdminMessage(msg=MessageChain([Plain(text="Pixiv:删除缓存图片失败")]))
