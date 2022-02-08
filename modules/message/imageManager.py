import requests
from modules.http.miraiHttpRequests import MiraiHttpRequests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from modules.utils import log as Log
from modules.conf import config
import os
import random
import json
import time
import traceback


class ImageManager:
    def __init__(self) -> None:
        self.httpRequest = MiraiHttpRequests()
        self.maxImgSize = int(config.getConf(section='mirai', option='maxImgSize'))

    def upload_img(self, file_path: str, image_type: str):
        """ 上传本地图片获取imageID

        Param:
            file_path (str): 本地图片路径
            image_type (str): friend,group或temp
        Returns:
            返回image_id,如果出错则返回false
        """
        # 过滤大于config中设定的图片最大size
        if os.path.getsize(file_path) > self.maxImgSize*1024*1024:
            return False

        multipart_encoder = MultipartEncoder(
            fields={
                'sessionKey': self.httpRequest.sessionKey,
                'type': image_type,
                'img': (os.path.basename(file_path),
                        open(file_path, 'rb'), 'application/octet-stream')
            },
            boundary='-----------------------------' +
            str(random.randint(1e28, 1e29 - 1))
        )

        headers = {'Content-Type': multipart_encoder.content_type}
        response = self.httpRequest.request.post(
            '%s/%s' % (self.httpRequest.host, 'uploadImage'), data=multipart_encoder, headers=headers)
        response.raise_for_status()
        image_json = json.loads(response.text)
        if 'imageId' in image_json:
            Log.info(msg=f"[Mirai][Image] upload image success,imageId: {image_json['imageId']}")
            return image_json['imageId']
        else:
            Log.error(msg=f"[Mirai][Image] upload image failed,filePath: {file_path}")
            Log.error(msg=response.text)
            return False

    def upload_img_from_url(self, url: str, image_type: str):
        """ 根据url地址上传互联网图片获取imageID

        Param:
            url (str): 图片的互联网地址
            image_type (str): friend,group或temp
        Returns:
            返回image_id,如果出错则返回false
        """
        temp_path = os.path.join('modules/resource', 'temp')
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        img_save_path = os.path.join(
            temp_path, 'temp%d.png' % int(time.time()))
        try:
            img = requests.get(url)
            with open(img_save_path, 'wb') as f:
                f.write(img.content)
                f.flush()

        except Exception:
            Log.error(msg=traceback.format_exc())
            return False

        if os.path.exists(img_save_path):
            image_id = self.upload_img(
                image_type=image_type, file_path=img_save_path)

            os.remove(img_save_path)
            return image_id
        else:
            Log.error('download image error')
            return False
