#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 群员消息撤回事件
@Date     :2022/03/29 09:11:22
@Author      :yuejieyao
@version      :1.0
"""

import os
import random

from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image
from ..miraiEvent import MiraiEventProcessor


@MiraiEventProcessor.mirai_group_recall_register('GroupRecall')
class GroupRecall:
    NAME = "群员消息撤回事件"
    DESCRIPTION = """围观"""

    def process(self, group: int, qq: int, message_id: int):
        resource_path = os.path.join('modules/resource', 'img/recall')
        img_path = os.path.join(resource_path, "%d.jpg" % random.randint(1, 5))
        msg = MessageChain([Image(image_type='group', file_path=img_path)])
        MiraiMessageRequest().sendGroupMessage(msg=msg, target=group)
