#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 摸鱼人日历(https://api.vvhan.com/api/moyu?type=json)
@Date     :2022/04/20 10:54:20
@Author      :yuejieyao
@version      :1.0
"""
import uuid
from datetime import datetime, timedelta
from io import BytesIO

from PIL import Image as PILImage

import requests

from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from ..miraiSchedule import MiraiScheduleProcessor


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('Calendar', 8, 30)
class Calendar:
    NAME = "摸鱼人日历"
    DESCRIPTION = "每日早上8点半触发发送摸鱼人日历"

    def process(self):
        msg_req = MiraiMessageRequest()
        try:
            msg = get_news_img()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                if MiraiDataSource().isScheduleClose(register_name='Calendar', group=group.id):
                    continue
                msg_req.sendGroupMessage(msg=msg, target=group.id)
        except:
            msg = MessageChain([Plain(text="调用摸鱼人日历失败,将在5分钟后重新调用")])
            msg_req.sendAdminMessage(msg=msg)

            MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                run_date=datetime.now() + timedelta(minutes=5), func=self.process)


def get_news_img() -> MessageChain:
    resp = requests.session().get('https://api.j4u.ink/v1/store/other/proxy/remote/moyu.json')
    resp.raise_for_status()
    result = resp.json()
    if 'code' in result and result['code'] == 200:
        img_url = result['data']['moyu_url']

        # 这个api返回的url文件后缀是png,但是不知道啥时候API更新后会跳转成一个webp,由于QQ不支持,需要先转换一下
        file_type = 'png'
        resp = requests.session().get(img_url)
        if resp.history:
            file_type = resp.url.split('.')[-1]
        if file_type == 'png':
            msg = MessageChain([Image(image_type="group", image_url=result['data']['moyu_url'])])
        else:
            # 将图片转为png格式
            img = PILImage.open(BytesIO(resp.content)).convert('RGBA')
            png_bytes = BytesIO()
            img.save(png_bytes, format='PNG')
            png_bytes.seek(0)

            # 将png格式的图像保存到本地
            path = f'modules/resource/temp/{uuid.uuid1()}.png'
            with open(path, 'wb') as f:
                f.write(png_bytes.read())
            msg = MessageChain([Image(image_type="group", file_path=path)])
        return msg
    else:
        raise Exception('Calendar:获取数据失败')
