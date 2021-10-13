
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 随机P站图,从排行榜抽,关注作者后主动推送,循环任务在schedule里
@Date     :2021/08/17 15:32:01
@Author      :yuejieyao
@version      :1.0
'''
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageType import Image, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.dataSource import DataSource
from modules.utils import log as Log
import traceback
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('pixiv')
class Pixiv:
    pixiv_db = 'modules/resource/data/pixiv.db'

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        message_display = chains.asDisplay()
        if re.match('图来.*', message_display) != None:
            ds = DataSource(path=self.pixiv_db)
            try:
                pic = ds.getRandomPic(group=group)
                msg = MessageChain([Plain(text="来了来了~\n"),
                                    Plain(text=f"title : {pic['title']}\n"),
                                    Plain(text=f"author : {pic['author']}({pic['user']})\n"),
                                    Plain(text=f"tags : {pic['tag']}\n"),
                                    Image(image_type='group', file_path=pic['path'])])
                MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
            except Exception:
                Log.error(msg=traceback.format_exc())
            else:
                ds.setSend(id=pic['id'], group=group)  # 记录已发送

        if re.match('关注作者 .*', message_display) != None:
            msgs = message_display.split(' ')
            if len(msgs) == 2:
                if msgs[1].isdigit():
                    ds = DataSource(path=self.pixiv_db)
                    try:
                        if ds.follow(user=int(msgs[1]), group=group, qq=target):
                            MiraiMessageRequest().sendGroupMessage(
                                msg=MessageChain([Plain(text=f"{target}关注作者{msgs[1]}成功,当有新作品时将主动推送")]), target=group, quote=quote)
                        else:
                            MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                                [Plain(text="关注失败")]), target=group, quote=quote)
                    except Exception:
                        Log.error(msg=traceback.format_exc())
                        MiraiMessageRequest().sendGroupMessage(
                            msg=MessageChain([Plain(text="关注失败")]), target=group, quote=quote)

        if re.match('取消关注 .*', message_display) != None:
            msgs = message_display.split(' ')
            if len(msgs) == 2:
                if msgs[1].isdigit():
                    ds = DataSource(path=self.pixiv_db)
                    try:
                        if ds.unfollow(user=int(msgs[1]), group=group, qq=target):
                            MiraiMessageRequest().sendGroupMessage(
                                msg=MessageChain([Plain(text=f"{target}取消关注作者{msgs[1]}成功")]), target=group, quote=quote)
                        else:
                            MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                                [Plain(text="取消关注失败")]), target=group, quote=quote)
                    except Exception as e:
                        Log.error(msg=traceback.format_exc())
                        MiraiMessageRequest().sendGroupMessage(
                            msg=MessageChain([Plain(text="取消关注失败")]), target=group, quote=quote)
