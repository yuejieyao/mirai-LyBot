from modules.http.miraiHttpRequests import MiraiHttpRequests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from enum import Enum
import os
import random
import json


class ImageType(Enum):
    Friend = 'friend'
    Group = 'group'
    Temp = 'temp'


class ImageManager(MiraiHttpRequests):
    def __init__(self) -> None:
        super().__init__()

    def upload_img(self, file_path: str, image_type: ImageType = ImageType.Group):
        multipart_encoder = MultipartEncoder(
            fields={
                'sessionKey': MiraiHttpRequests.SessionKey,
                'type': image_type,
                'img': (os.path.basename(file_path),
                        open(file_path, 'rb'), 'application/octet-stream')
            },
            boundary='-----------------------------' +
            str(random.randint(1e28, 1e29 - 1))
        )

        headers = {'Content-Type': multipart_encoder.content_type}
        try:
            response = self.request.post(
                '%s/%s' % (self.host, 'uploadImage'), data=multipart_encoder, headers=headers)
            response.raise_for_status()
            return json.loads(response.text)['imageId']
        except Exception as e:
            print('upload image error')
            print(e)
            return False
