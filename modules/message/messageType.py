from modules.resource.imageManager import ImageType, ImageManager


class MessageElement:
    def __init__(self) -> None:
        self.chain = {}

    def asDisplay(self) -> str:
        pass

    def asSerializationString(self) -> str:
        pass

    def fromJson():
        pass


class Source(MessageElement):
    type: str = 'Source'

    def __init__(self, id: int, time: int) -> None:
        self.chain = {'type': 'Source', 'id': id, 'time': time}
        self.id = id

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

    def __init__(self, file_path: str, image_id: str, image_url: str, image_type: ImageType) -> None:
        if all([file_path, image_id == None]):
            imageManager = ImageManager()
            image_id = imageManager.upload_img(
                file_path=file_path, image_type=image_type)
            self.chain = {'type': 'Image', 'imageId': self.image_id}
        elif all([image_id, image_url]):
            self.chain = {'type': 'Image',
                          'imageId': image_id, 'url': image_url}

    def asDisplay(self) -> str:
        return '[图片]'

    def asSerializationString(self) -> str:
        return f'[mirai:image:{self.image_id}]'

    @staticmethod
    def fromJson(obj) -> 'Image':
        return Image(image_id=obj['imageId'], image_url=obj['url'])


class MusicShare(MessageElement):
    type: str = 'MusicShare'

    def __init__(self) -> None:
        super().__init__()

    def asDisplay() -> str:
        pass

    def asSerializationString() -> str:
        pass
