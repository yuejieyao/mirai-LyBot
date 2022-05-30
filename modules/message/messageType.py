from modules.message.imageManager import ImageManager


class MessageElement:
    chain = None

    def __init__(self) -> None:
        pass

    def asDisplay(self) -> str:
        pass

    def asSerializationString(self) -> str:
        pass

    @staticmethod
    def fromJson(obj):
        pass


class Source(MessageElement):
    type: str = 'Source'

    def __init__(self, _id: int, time: int) -> None:
        super().__init__()
        self.chain = {'type': 'Source', 'id': _id, 'time': time}
        self.id = _id

    def asDisplay(self) -> str:
        return ''

    def asSerializationString(self) -> str:
        return ''

    @staticmethod
    def fromJson(obj) -> 'Source':
        return Source(obj['id'], obj['time'])


class At(MessageElement):
    type: str = 'At'

    def __init__(self, target: int) -> None:
        super().__init__()
        self.chain = {'type': 'At', 'target': target}
        self.target = target

    def asDisplay(self) -> str:
        return f"@{self.target}"

    def asSerializationString(self) -> str:
        return f"@[mirai:at:{self.target}]"

    @staticmethod
    def fromJson(obj) -> 'At':
        return At(obj['target'])


class AtAll(MessageElement):
    type: str = 'AtAll'

    def __init__(self) -> None:
        super().__init__()
        self.chain = {'type': 'AtAll'}

    def asDisplay(self) -> str:
        return '@全体成员'

    def asSerializationString(self) -> str:
        return "[mirai:atall]"

    @staticmethod
    def fromJson(obj) -> 'AtAll':
        return AtAll()


class Plain(MessageElement):
    type: str = 'Text'

    def __init__(self, text: str) -> None:
        super().__init__()
        self.chain = {'type': 'Plain', 'text': text}
        self.text = text

    def asDisplay(self) -> str:
        return self.text

    def asSerializationString(self) -> str:
        return self.text

    @staticmethod
    def fromJson(obj) -> 'Plain':
        return Plain(obj['text'])


class Image(MessageElement):
    type: str = 'Image'

    def __init__(self, image_type: str, file_path: str = None, image_id: str = None, image_url: str = None) -> None:
        """ 生成图片消息

        Param:
            image_type (str): friend,group或temp
            file_path (str): 可选,若是本地上传图片则需要此参数
            image_id (str): 可选,若已有image_id则直接生成图片消息
            image_url (str): 可选,若从网络图片生成消息则需要此参数
        Returns:
            Image: 图片消息
        """

        super().__init__()
        if file_path is not None and image_id is None:
            # 本地图片上传
            image_manager = ImageManager()
            image_id = image_manager.upload_img(
                file_path=file_path, image_type=image_type)
            self.chain = {'type': 'Image', 'imageId': image_id}
        elif image_id is None and image_url is not None:
            # 网络图片下载后上传
            image_manager = ImageManager()
            image_id = image_manager.upload_img_from_url(
                image_url, image_type=image_type)
            self.chain = {'type': 'Image', 'imageId': image_id}
        elif image_id is not None and image_url is not None:
            # 已上传的图片
            self.chain = {'type': 'Image',
                          'imageId': image_id, 'url': image_url}
        self.image_id = image_id

    def asDisplay(self) -> str:
        return '[图片]'

    def asSerializationString(self) -> str:
        return f'[mirai:image:{self.image_id}]'

    @staticmethod
    def fromJson(obj) -> 'Image':
        return Image(image_id=obj['imageId'], image_url=obj['url'], image_type='temp')


class MusicShare(MessageElement):
    type: str = 'MusicShare'

    def __init__(self, kind: str, title: str, summary: str, jump_url: str, picture_url: str, music_url: str,
                 brief: str) -> None:
        """ 音乐卡片分享
        
        Param:
            kind (str):只能是NeteaseCloudMusic等几个,具体参考mirai文档
            title (str): 标题
            summary (str): 简介
            jumpUrl (str): 跳转地址
            pictureUrl (str): 封面图片地址
            musicUrl (str): 音乐地址
            brief (str): 说明
        """

        super().__init__()
        self.chain = {
            'type': 'MusicShare',
            'kind': kind,
            'title': title,
            'summary': summary,
            'jumpUrl': jump_url,
            'pictureUrl': picture_url,
            'musicUrl': music_url,
            'brief': brief
        }

    def asDisplay(self) -> str:
        pass

    def asSerializationString(self) -> str:
        pass


class App(MessageElement):
    type: str = 'App'
    content: str

    def __init__(self, content: str) -> None:
        super().__init__()
        self.chain = {'type': 'App', content: str}
        self.content = content

    def asDisplay(self) -> str:
        return "[APP消息]"

    def asSerializationString(self) -> str:
        return "[mirai:App]"

    @staticmethod
    def fromJson(obj) -> 'App':
        return App(content=obj['content'])


class Xml(MessageElement):
    type: str = 'Xml'
    xml: str

    def __init__(self, xml: str) -> None:
        super().__init__()
        self.chain = {'type': 'Xml', 'xml': xml}
        self.xml = xml

    def asDisplay(self) -> str:
        return "[Xml消息]"

    def asSerializationString(self) -> str:
        return "[mirai:Xml]"

    @staticmethod
    def fromJson(obj) -> 'Xml':
        return Xml(xml=obj['xml'])
