import traceback
from typing import List, Type

from modules.message.messageType import MessageElement, Source, Plain, Image, At, AtAll, App, Xml
from modules.utils import log


class MessageChain:
    def __init__(self, elements=None) -> None:
        if elements is None:
            elements = []
        self.elements = elements
        self.prev = None

    def append(self, element: MessageElement) -> None:
        """ 添加一个MessageElement元素到末尾

        Param:
            element (MessageElement):如Plain,Image等
        """

        self.elements.append(element)

    def extend(self, elements: List[MessageElement]) -> None:
        """ 添加多个MessageElement元素到末尾

        Param:
            elements (List[MessageElement]):多个MessageElement组成的List
        """

        self.elements.extend(elements)

    def setPrev(self, prev: 'MessageChain') -> None:
        self.prev = prev

    def getPrev(self) -> 'MessageChain':
        return self.prev

    def asDisplay(self, has_at=True) -> str:
        if has_at:
            return ''.join(i.asDisplay() for i in self.elements)
        else:
            return ''.join(i.asDisplay() for i in self.elements if not isinstance(i, At))

    def asSerializationString(self) -> str:
        return ''.join(i.asSerializationString() for i in self.elements)

    def asJson(self) -> list:
        chains = [i.chain for i in self.elements]
        return chains

    def getId(self) -> int:
        """ 从Mirai得到的MessageChain第一个MessageElement固定是Source,对应了此MessageChain的ID,通过此方法获取ID """
        if isinstance(self.elements[0], Source):
            return self.elements[0].id
        return 0

    def get(self, element_type: Type[MessageElement]) -> List[Type[MessageElement]]:
        """获取消息中对应类型的元素

        Param:
            element_type (MessageElement): 对应的消息类型,如Plain,Image
        Returns:
            List[MessageElement]: 对应类型的元素列表
        """

        return [i for i in self.elements if type(i) is element_type]

    def has(self, element_type: Type[MessageElement]) -> bool:
        return element_type in [type(i) for i in self.elements]

    @staticmethod
    def fromJsonList(obj_list: List) -> 'MessageChain':
        """ 根据消息的json数据生成MessageChain,主要用于websocket的on_message事件 """

        _list = []
        for obj in obj_list:
            try:
                if obj['type'] in ['Source', 'Plain', 'Image', 'At', 'AtAll', 'App', 'Xml']:
                    _list.append(
                        getattr(eval(obj['type']), 'fromJson')(obj))
                    # 生成对应Type的MessageElement
            except:
                log.error(msg=traceback.format_exc())
                continue
        return MessageChain(_list)

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.elements[key]
        elif isinstance(key, slice):
            return self.__class__(self.elements[key])
        elif issubclass(key, MessageElement):
            return self.get(key)
        else:
            raise NotImplementedError
