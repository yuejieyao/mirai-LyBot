#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: AI作图
@Date: 2022/10/10 10:02
@Author: yuejieyao
@version: 1.0
"""

import os
import re
import uuid
import traceback
import time
import random
import requests
import base64
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from .modules.utils.novelAIUtils import NovelAIUtils
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.utils import log
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('NovelAI')
class NovelAI:
    NAME = 'AI作图'
    DESCRIPTION = '发送: 作图 关键词(逗号分割多个关键词)'

    directory = "modules/resource/illusts"

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay()
        if re.match('作图 .*', msg_display) is not None:
            if ' -s ' in msg_display:
                i = msg_display.find('-s') + 3
                j = msg_display.find(' ', i)
                seed = int(msg_display[i:j])
                keywords = msg_display[j + 1:]

            else:
                msg_split = msg_display.split(' ', 1)
                keywords = msg_split[1]
                keywords = keywords.replace('，', ',')
                seed = round(time.time() / 10) + random.randint(1, 99)

            if not NovelAIUtils.hasZHChar(keywords):
                msg_req = MsgReq()
                msg_req.sendGroupMessage(msg=MessageChain([Plain(text="正在请求绘制...")]), target=group)
                fname = f"{uuid.uuid1()}.png"
                path = os.path.join(self.directory, fname)
                try:
                    if NovelAIUtils().createImg(seed, keywords, self.directory, fname):
                        log.info('[Plugins][NovelAI] create Img success, keywords=' + keywords)
                        msg = MessageChain([Plain(text="seed: %s\n" % seed)])
                        img = Image(image_type='group', file_path=path)
                        if img.image_id:
                            msg.append(img)
                            msg_req.sendGroupMessage(msg=msg, target=group)
                except:
                    log.error(msg=traceback.format_exc())
        elif re.match('以图作图 .*', msg_display) is not None:
            if ' -s ' in msg_display:
                i = msg_display.find('-s') + 3
                j = msg_display.find(' ', i)
                seed = int(msg_display[i:j])
                keywords = msg_display[j + 1:]

            else:
                msg_split = msg_display.split(' ', 1)
                keywords = msg_split[1]
                keywords = keywords.replace('，', ',')
                seed = round(time.time() / 10) + random.randint(1, 99)
            fname = f"{uuid.uuid1()}.png"
            path = os.path.join(self.directory, fname)

            def _filter(_msg: MessageChain, _target: int, _group: int):
                if _target == target and _group == group:
                    return True
                return False

            def _callback(_msg: MessageChain, _target: int, _group: int):
                if not _msg.has(Image):
                    return
                try:
                    _img = _msg.get(Image)[0]
                    res = requests.get(_img.chain['url']).content
                    base64_data = base64.b64encode(res)
                    if NovelAIUtils().createImgByImg(base64_data, seed, keywords, self.directory, fname):
                        log.info('[Plugins][NovelAI] create Img success,base_img= %s ,keywords= %s' % (
                            _img.chain['url'], keywords))
                        __msg = MessageChain([Plain(text="seed: %s\n" % seed)])
                        __img = Image(image_type='group', file_path=path)
                        if __img.image_id:
                            __msg.append(__img)
                            MsgReq().sendGroupMessage(msg=__msg, target=_group)
                except:
                    log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(
                MiraiMessageMonitor(monitor_type='GroupMessage', target=target, call_filter=_filter,
                                    call_func=_callback))  # 添加一次性监听
