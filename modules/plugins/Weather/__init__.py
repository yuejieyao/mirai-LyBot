#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 实时天气查询,调用格式: 天气 无锡
@Date     :2021/07/22 15:36:06
@Author      :yuejieyao
@version      :1.0
"""
import os
import re
import uuid

import requests
from PIL import Image as Img, ImageDraw, ImageFont

from modules.conf import config
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor

font_file = os.path.join(os.path.dirname(
    __file__), 'style/AdobeHeitiStd-Regular.otf')
icon_file = os.path.join(os.path.dirname(__file__), 'color-64')


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Weather')
class Weather:
    NAME = "天气查询"
    DESCRIPTION = """发送:天气 地名"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        message_display = chains.asDisplay()
        if re.match('天气 .*', message_display) is None:
            return
        msgs = message_display.split(' ')
        if len(msgs) == 2:
            msg_req = MiraiMessageRequest()
            try:
                now = getWeather(msgs[1])
                image_path = weatherMsgCreator(obj=now, location=msgs[1])
                msg = MessageChain(
                    [Image(image_type='group', file_path=image_path)])
                msg_req.sendGroupMessage(msg=msg, target=group, quote=quote)
            except:
                msg = MessageChain([Plain(text="天气查询失败")])
                msg_req.sendGroupMessage(msg=msg, target=group, quote=quote)


def getLonlat(location: str) -> str:
    api_key = config.getConf('qweather', 'apiKey')
    url = f"https://geoapi.qweather.com/v2/city/lookup?key={api_key}&location={location}"
    resp = requests.session().get(url)
    resp.raise_for_status()
    result = resp.json()
    if result['code'] == '200':
        location = result['location'][0]
        lonlat = location['lon'] + ',' + location['lat']
        return lonlat
    else:
        raise Exception("Weather:获取城市定位数据失败")


def getWeather(location: str):
    lonlat = getLonlat(location=location)
    api_key = config.getConf('qweather', 'apiKey')
    url = f"https://devapi.qweather.com/v7/weather/now?key={api_key}&location={lonlat}"
    resp = requests.session().get(url)
    resp.raise_for_status()
    result = resp.json()
    if result['code'] == '200':
        return result['now']
    else:
        raise Exception("Weather:获取天气数据失败")


def weatherMsgCreator(obj, location: str) -> str:
    """根据天气信息生成图片,返回path"""
    temp = obj['temp']  # 温度
    icon = obj['icon']  # 对应图标
    text = obj['text']  # 文字描述
    wind_dir = obj['windDir']  # 风向
    wind_scale = obj['windScale']  # 风力
    humidity = obj['humidity']  # 湿度

    width = 210
    height = 21 * 5

    image = Img.new('RGBA', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, 14)
    draw.text((85, 5), f"天气状态: {text}", font=font, fill='#000000')
    draw.text((85, 25), f"当前气温: {temp}", font=font, fill='#000000')
    draw.text((85, 45), f"风向: {wind_dir}", font=font, fill='#000000')
    draw.text((85, 65), f"风力等级: {wind_scale}", font=font, fill='#000000')
    draw.text((85, 85), f"湿度: {humidity}", font=font, fill='#000000')
    (x, y) = (25, 15)
    if len(location) > 5:
        x = 0
    else:
        x = 25 - (len(location) - 2) * 5
    # 地名太长打印会覆盖后边,懒得改了,一般4个字以内效果还行
    draw.text((x, y), location, font=font, fill="#000000")
    icon_image = Img.open(f'{icon_file}/{icon}.png').convert('RGBA')
    image.paste(icon_image, box=(5, 30), mask=icon_image)
    temp_path = os.path.join(os.path.dirname(__file__), 'cache')
    if not os.path.exists(temp_path):
        os.mkdir(temp_path)
    path = os.path.join(temp_path, f'{uuid.uuid1()}.png')
    image.save(path)
    return path
