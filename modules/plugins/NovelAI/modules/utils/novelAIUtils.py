#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 
@Date: 2022/10/10 10:46
@Author: yuejieyao
@version: 1.0
"""
import base64
import os.path
import requests
import time
import random
from typing import Tuple
from enum import Enum

from modules.conf import config


class SamplerType(Enum):
    k_euler_ancestral = 1
    k_euler = 2
    k_lms = 3


class NovelAIUtils:
    MAX_OUTPUT_PIXELS = 1048576
    DEFAULT_UC = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    def __init__(self):
        self.url = "https://api.novelai.net"
        self.token = config.getConf('novel_ai', 'token')
        self.headers = {"authorization": 'Bearer ' + self.token,
                        "authority": 'api.novelai.net',
                        "path": '/ai/generate-image',
                        'content-type': 'application/json',
                        "referer": 'https://novelai.net/',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', }

    def createImg(self, keywords: str, path: str, fname: str, width: int = 512, height: int = 768,
                  scale: float = 12, steps: int = 28, sampler: str = SamplerType(1).name, uc: str = DEFAULT_UC,
                  seed: int = None, img: bytes = None):
        if not seed:
            seed = round(time.time() / 10) + random.randint(1, 99)

        data = {
            "input": "masterpiece, best quality, " + keywords,
            "model": "safe-diffusion",
            "parameters": {
                "width": width,
                "height": height,
                "scale": scale,
                "sampler": sampler,
                "steps": steps,
                "seed": seed,
                "n_samples": 1,
                "ucPreset": 0,
                "qualityToggle": True,
                "uc": uc
            }
        }

        if img:
            data["parameters"]["image"] = img.decode('ascii')
            data["parameters"]["steps"] = 50
            data["parameters"]["strength"] = 0.7
            data["parameters"]["noise"] = 0.2

        resp = requests.post(self.url + '/ai/generate-image', json=data, headers=self.headers)
        resp.raise_for_status()
        res = resp.text[27:]
        with open(os.path.join(path, fname), 'wb') as out_file:
            out_file.write(base64.b64decode(res))
        return seed

    # def createImgByImg(self, img: bytes, seed: int, keywords: str, path: str, fname: str):
    #     data = {
    #         "input": "masterpiece, best quality, " + keywords,
    #         "model": "safe-diffusion",
    #         "parameters": {
    #             "image": img.decode('ascii'),
    #             "width": 512,
    #             "height": 768,
    #             "scale": 11,
    #             "sampler": "k_euler_ancestral",
    #             "steps": 50,
    #             "seed": seed,
    #             "n_samples": 1,
    #             "ucPreset": 0,
    #             "strength": 0.7,
    #             "noise": 0.2,
    #             "qualityToggle": True,
    #             "uc": "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
    #         }
    #     }
    #     resp = requests.post(self.url + '/ai/generate-image', json=data, headers=self.headers)
    #     resp.raise_for_status()
    #     res = resp.text[27:]
    #     with open(os.path.join(path, fname), 'wb') as out_file:
    #         out_file.write(base64.b64decode(res))
    #     return True

    @staticmethod
    def hasZHChar(chars: str):
        for char in chars:
            if u'\u4e00' <= char <= u'\u9fa5':
                return True
        return False

    @staticmethod
    def isSizeValid(size: Tuple[int, int]):
        width, height = size
        if width % 64 == 0 and height % 64 == 0 and width * height <= NovelAIUtils.MAX_OUTPUT_PIXELS:
            return True
        return False

    @staticmethod
    def getValidSize(size: Tuple[int, int]):
        width, height = size
        if width % 64 > 0:
            width -= width % 64
        if height % 64 > 0:
            height -= height % 64
        while width * height > NovelAIUtils.MAX_OUTPUT_PIXELS:
            width -= 64
            height -= 64
        return width, height
