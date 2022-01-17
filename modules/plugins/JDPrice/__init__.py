#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: JD商品价格监控
@Date     :2022/01/14 13:26:41
@Author      :yuejieyao
@version      :1.0
'''
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Image, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.dataSource import DataSource
from modules.utils import log as Log, common
import traceback
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('JDPrice')
class JDPrice:
    NAME = "JD商品价格监控"
    DESCRIPTION = """关注商品 商品ID
    查看购物车
    删除商品 商品ID
    """

    jd_db = 'modules/resource/data/jd.db'

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        msg_display = chains.asDisplay()
        p_add = "(添加商品|关注商品|加商品|\+商品|add goods|\+goods|addgoods)\s*\d*"
        p_del = "(删除商品|删商品|\-商品|del goods|\-goods|delgoods)\s*\d*"
        if re.match(p_add, msg_display):
            try:
                goods_id = int(list(filter(None, re.findall("\d*", msg_display)))[0])
                ds = DataSource(path=self.jd_db)
                if not ds.existsFollow(goods_id=goods_id, group=group, qq=target):
                    ds.addFollow(goods_id=goods_id, group=group, qq=target)
                    url, path = ds.create_current_img(goods_id)
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f"成功加入购物车~\n商品当前信息如下:\n商品地址:{url}\n"), Image(
                        image_type='group', file_path=path)]), target=group, quote=quote)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="您已添加该商品,请勿重复添加")]), target=group, quote=quote)

            except:
                Log.error(msg=traceback.format_exc())
        elif msg_display in ['查看商品', '看商品', '查看购物车', '看购物车', 'showgoods', 'show goods']:
            try:
                ds = DataSource(path=self.jd_db)
                res = ds.getFollow(group=group, qq=target)
                if len(res) > 0:
                    content = '\n'.join([f"({goods[0]}) {goods[1]}" for goods in res])
                    ids = ','.join([goods[0] for goods in res])
                    msg = MessageChain([Plain("您购物车中的商品如下:\n"), Image(
                        image_type='group', file_path=common.text_to_img(content)), Plain(text=f'\n供您复制的ID:{ids}')])
                    MMR().sendGroupMessage(msg=msg, target=group, quote=quote)

                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="您尚未添加过商品")]), target=group, quote=quote)

            except:
                Log.error(msg=traceback.format_exc())

        elif re.match(p_del, msg_display):
            try:
                goods_id = int(list(filter(None, re.findall("\d*", msg_display)))[0])
                ds = DataSource(path=self.jd_db)
                if ds.existsFollow(goods_id=goods_id, group=group, qq=target):
                    if ds.removeFollow(goods_id=goods_id, group=group, qq=target):
                        MMR().sendGroupMessage(msg=MessageChain([Plain(text="删除成功")]), target=group, quote=quote)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="您尚未添加该商品")]), target=group, quote=quote)
            except:
                Log.error(msg=traceback.format_exc())
