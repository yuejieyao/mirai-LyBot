#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:点歌(网易云音乐),调用格式:点歌 歌名
@Date     :2021/07/20 13:14:19
@Author      :yuejieyao
@version      :1.0
"""

import re

import requests

from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, MusicShare
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('NeMusicShare')
class NeMusicShare:
    NAME = "点歌"
    DESCRIPTION = """发送内容:点歌 歌名"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        if re.match('点歌 .*', chains.asDisplay()) is not None:
            msg_req = MiraiMessageRequest()
            msgs = chains.asDisplay().split(' ')
            if len(msgs) == 2:
                keyword = msgs[1]
                msg_req.sendGroupMessage(msg=getMusic(
                    keyword=keyword), target=group)
            else:
                msg_req.sendGroupMessage(msg=MessageChain(Plain(text="不支持的格式\n示例:点歌 宁夏")), target=group)


def getMusic(keyword: str) -> MessageChain:
    try:
        __api_url = "https://autumnfish.cn/search?keywords=%s" % keyword
        resp = get(__api_url)
        result = resp.json()
        if 'result' in result and 'songs' in result['result']:
            __music_id = result['result']['songs'][0]['id']
            __album_id = result['result']['songs'][0]['album']['id']
            __api_url = "https://autumnfish.cn/album?id=%s" % __album_id
            resp = get(__api_url)
            result = resp.json()
            if 'code' in result and result['code'] == 200:
                temp_music = filter(
                    lambda x: x['id'] == __music_id, result['songs'])
                music = list(temp_music)[0]
                title = music['name']
                summary = ','.join([x['name']
                                    for x in result['album']['artists']])
                jump_url = 'https://y.music.163.com/m/song/%s' % music['id']
                picture_url = result['album']['picUrl']
                music_url = 'https://music.163.com/song/media/outer/url?id=%s.mp3' % music['id']
                brief = '[分享]%s' % title
                msg = MessageChain([MusicShare(kind='NeteaseCloudMusic', title=title, summary=summary,
                                               jump_url=jump_url, picture_url=picture_url, music_url=music_url,
                                               brief=brief)])
                return msg
            else:
                msg = MessageChain(
                    [Plain(text=f"未能正常返回数据:{__api_url}")])
                return msg

        else:
            msg = MessageChain(
                [Plain(text=f"未能正常返回数据:{__api_url}")])
            return msg

    except:
        msg = MessageChain(
            [Plain(text="MusicShare Error")])
        return msg


def get(url: str) -> requests.Response:
    resp = requests.session().get(url=url)
    resp.raise_for_status()
    return resp
