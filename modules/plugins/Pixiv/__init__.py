
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 随机P站图,从排行榜抽,关注作者后主动推送,循环任务在schedule里
@Date     :2021/08/17 15:32:01
@Author      :yuejieyao
@version      :1.0
'''
import traceback
import uuid
import os
import re
import random
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Image, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.dataSource import DataSource
from modules.utils import log as Log


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Pixiv')
class Pixiv:
    NAME = "色图(Pixiv)"
    DESCRIPTION = """抽图发送:图来
    如要添加发送:关注作者 作者ID
    取消关注发送:取消关注 作者ID
    屏蔽作者发送:屏蔽作者 作者ID
    取消屏蔽发送:取消屏蔽 作者ID
    """

    pixiv_db = 'modules/resource/data/pixiv.db'
    directory = "modules/resource/illusts"

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        message_display = chains.asDisplay()
        if re.match('图来.*', message_display) != None:
            if random.random() <= 0.1:
                # 1成概率傲娇
                MMR().sendGroupMessage(msg=MessageChain(
                    [Plain(text=str(random.choice(['不要!', '不给!', '不许涩涩!', '就不!'])))]), target=group)
                return
            try:
                ds = DataSource(path=self.pixiv_db)
                pic = ds.getRandomPic(group=group)

                fname = f"{uuid.uuid1()}.png"
                path = os.path.join(self.directory, fname)

                if not os.path.exists(path=path):
                    if ds.pixiv.downImg(url=pic['url'], path=self.directory, name=fname):
                        Log.info(f"[Plugins][Pixiv] download IMG[{pic['id']}(ID)][{path}(Path)] success")

                msg = MessageChain([Plain(text="来了来了~\n"),
                                    Plain(text=f"title : {pic['title']}({pic['id']})\n"),
                                    Plain(text=f"author : {pic['author']}({pic['user']})\n"),
                                    Plain(text=f"tags : {pic['tag']}\n")])
                img = Image(image_type='group', file_path=path)
                if img.image_id:
                    msg.append(img)
                    MMR().sendGroupMessage(msg=msg, target=group)
            except Exception:
                Log.error(msg=traceback.format_exc())
            else:
                ds.setSend(id=pic['id'], group=group)  # 记录已发送
                ds.close()

        elif re.match('(关注作者|关注画师|follow author)\s*\d*', message_display) != None:
            try:
                author_id = int(list(filter(None, re.findall("\d*", message_display)))[0])
                ds = DataSource(path=self.pixiv_db)
                if ds.follow(user=author_id, group=group, qq=target):
                    MMR().sendGroupMessage(
                        msg=MessageChain([Plain(text=f"{target}关注作者{author_id}成功,当有新作品时将主动推送,如需取消可输入:取消关注 作者ID")]), target=group)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="关注失败")]), target=group, quote=quote)
            except:
                Log.error(msg=traceback.format_exc())

        elif re.match('(取消关注|取消关注作者|取消关注画师|unfollow author)\s*\d*', message_display) != None:
            try:
                author_id = int(list(filter(None, re.findall("\d*", message_display)))[0])
                ds = DataSource(path=self.pixiv_db)

                if ds.unfollow(user=author_id, group=group, qq=target):
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f"{target}取消关注作者{author_id}成功")]), target=group)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="取消关注失败")]), target=group, quote=quote)
            except:
                Log.error(msg=traceback.format_exc())

        elif re.match('(屏蔽作者|屏蔽画师)\s*\d*', message_display) != None:
            try:
                author_id = int(list(filter(None, re.findall("\d*", message_display)))[0])
                ds = DataSource(path=self.pixiv_db)
                if ds.isBan(id=author_id):
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="已屏蔽该作者")]), target=group)
                else:
                    ds.setBan(id=author_id)
                    MMR().sendGroupMessage(
                        msg=MessageChain([Plain(text=f"屏蔽作者{author_id}成功,图库更新时将不再获取该作者的图片,如需取消可以输入:取消屏蔽 作者ID")]), target=group)
            except:
                Log.error(msg=traceback.format_exc())

        elif re.match('取消屏蔽\s*\d*', message_display) != None:
            try:
                author_id = int(list(filter(None, re.findall("\d*", message_display)))[0])
                ds = DataSource(path=self.pixiv_db)
                if ds.isBan(id=author_id):
                    ds.cancelBan(id=author_id)
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f"取消屏蔽作者{author_id}成功")]), target=group)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f"并没有屏蔽作者{author_id}")]), target=group)
            except:
                Log.error(msg=traceback.format_exc())

        elif re.match('删除关注\s*\d*', message_display) != None:
            try:
                author_id = int(list(filter(None, re.findall("\d*", message_display)))[0])
                ds = DataSource(path=self.pixiv_db)
                if ds.removeFollow(user=author_id):
                    MMR().sendGroupMessage(
                        msg=MessageChain([Plain(text=f"已删除所有作者ID = {author_id}的关注")]), target=group, quote=quote)
            except:
                Log.error(traceback.format_exc())
