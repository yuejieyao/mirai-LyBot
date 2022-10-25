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
from .modules.utils.novelAIUtils import NovelAIUtils, SamplerType
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.utils import log
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler


def getParam(command: str, name: str, split=' '):
    i = command.find(name) + len(name) + 1
    j = command.find(split, i)
    return command[i:j]


def getKwargs(command: str):
    if '-prompt' not in command:
        raise Exception("命令格式不正确,请使用:-prompt tag1,tag2,tag3 来增加正面提示tag")
    kwargs = {}
    if '-seed' in command:
        try:
            kwargs['seed'] = int(getParam(command, '-seed'))
        except:
            raise Exception("seed格式不正确,请使用:-seed 1234567 来设定图片的种子")
    if '-step' in command:
        try:
            kwargs['steps'] = int(getParam(command, '-step'))
        except:
            raise Exception("step格式不正确,请使用:-step 28 来设定AI生成图片使用的步数")
    if '-size' in command:
        size_str = getParam(command, '-size')
        size_split = re.split('[xX*]', size_str)
        if len(size_split) != 2:
            raise Exception("size格式不正确,请使用大写或小写的字母X,或*来分割宽高,如: -size 512*768")
        else:
            width, height = NovelAIUtils.getValidSize((int(size_split[0]), int(size_split[1])))
            kwargs['width'] = width
            kwargs['height'] = height
    if '-scale' in command:
        try:
            kwargs['scale'] = float(getParam(command, '-scale'))
        except:
            raise Exception("scale格式不正确,请使用: -scale 12 来设定AI的服从度")
    if '-sampler' in command:
        try:
            n = int(getParam(command, '-sampler'))
            kwargs['sampler'] = SamplerType(n).name
        except:
            raise Exception('sampler参数不正确,可选值为1-3,分别对应k_euler_ancestral,k_euler和k_lms三种采样模式')
    if '-uc' in command:
        kwargs['uc'] = getParam(command, '-uc', '-')
    kwargs['keywords'] = command[command.find('-prompt') + 8:]
    if NovelAIUtils.hasZHChar(kwargs['keywords']):
        raise Exception('prompt参数不正确,请不要包含中文')
    return kwargs


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('NovelAI')
class NovelAI:
    NAME = 'AI作图'
    DESCRIPTION = '发送: ci/cii -prompt 关键词(逗号分割多个关键词)'

    directory = "modules/resource/illusts"

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay()
        if msg_display in ['ci -h', 'cii -h']:
            msg = MessageChain([Plain('基础命令: ci/cii -prompt tag1,tag2,tag3,tag4 \n'),
                                Plain('ci命令根据tag生成图片,cii命令以图生图'),
                                Plain('可在ci/cii后,-prompt前增加附加指令: \n'),
                                Plain('    使用固定的种子,默认随机: -seed 1234567\n'),
                                Plain('    使用设定的步数,默认28,上传图片固定50: -step 28\n'),
                                Plain('    生成自定义大小的图片,默认512*768: -size 512x768\n'),
                                Plain('    设定AI的服从度,默认12: -scale 12\n'),
                                Plain('    使用其他采样模式,默认为1,可选值1-3分别对应k_euler_ancestral,k_euler和k_lms : -sampler 1\n'),
                                Plain('    使用自定义的负面tag,默认为官网设定的自带tag: -uc tag1,tag2,tag3\n')
                                ])
            MsgReq().sendGroupMessage(msg=msg, target=group)
        elif msg_display == 'ci -m':
            MsgReq().sendGroupMessage(
                MessageChain([Plain('ci -step 28 -size 512*768 -scale 12 -sampler 1 -prompt tag')]),
                target=group)
        elif msg_display == 'cii -m':
            MsgReq().sendGroupMessage(
                MessageChain([Plain('cii -size 512*768 -scale 12 -sampler 1 -prompt tag')]),
                target=group)
        elif re.match('ci .*', msg_display) is not None:
            msg_req = MsgReq()
            try:
                kwargs = getKwargs(msg_display[3:])
            except Exception as e:
                msg_req.sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group, quote=quote)
                return

            msg_req.sendGroupMessage(msg=MessageChain([Plain(text="正在请求绘制...")]), target=group)
            fname = f"{uuid.uuid1()}.png"
            path = os.path.join(self.directory, fname)
            try:
                if seed := NovelAIUtils().createImg(path=self.directory, fname=fname, **kwargs):
                    log.info('[Plugins][NovelAI] create Img success, keywords=' + kwargs['keywords'])
                    msg = MessageChain([Plain(text="seed: %s\n" % seed)])
                    img = Image(image_type='group', file_path=path)
                    if img.image_id:
                        msg.append(img)
                        msg_req.sendGroupMessage(msg=msg, target=group)
            except:
                log.error(msg=traceback.format_exc())
        elif re.match('cii .*', msg_display) is not None:
            try:
                kwargs = getKwargs(msg_display[3:])
            except Exception as e:
                MsgReq().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group, quote=quote)
                return

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
                    _msg_req = MsgReq()
                    _msg_req.sendGroupMessage(msg=MessageChain([Plain(text="正在请求绘制...")]), target=_group)
                    if _seed := NovelAIUtils().createImg(path=self.directory, fname=fname, img=base64_data, **kwargs):
                        log.info('[Plugins][NovelAI] create Img success,base_img= %s ,keywords= %s' % (
                            _img.chain['url'], kwargs['keywords']))
                        __msg = MessageChain([Plain(text="seed: %s\n" % _seed)])
                        __img = Image(image_type='group', file_path=path)
                        if __img.image_id:
                            __msg.append(__img)
                            _msg_req.sendGroupMessage(msg=__msg, target=_group)
                except:
                    log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(
                MiraiMessageMonitor(monitor_type='GroupMessage', target=target, call_filter=_filter,
                                    call_func=_callback))  # 添加一次性监听
