from typing import Any, Dict, List, Type, Union, TypeVar
from modules.message.messageType import MessageElement, Source, Plain, Image, At, AtAll, App, Xml
import copy


class MessageChain:
    def __init__(self, elements: List[MessageElement] = []) -> None:
        self.elements = elements

    def append(self, element: MessageElement) -> None:
        self.elements.append(element)

    def extend(self, elements: List[MessageElement]) -> None:
        self.elements.extend(elements)

    def asDisplay(self) -> str:
        return ''.join(i.asDisplay() for i in self.elements)

    def asSerializationString(self) -> str:
        return ''.join(i.asSerializationString() for i in self.elements)

    def asJson(self) -> Dict[str, Any]:
        chains = [i.chain for i in self.elements]
        return chains

    def getId(self) -> int:
        if isinstance(self.elements[0], Source):
            return self.elements[0].id
        return 0

    def get(self, element_type: MessageElement) -> List[MessageElement]:
        """获取消息中对应类型的元素
        Param:
            element_type (MessageElement): 对应的消息类型,如Plain,Image
        Returns:
            List[MessageElement]: 对应类型的元素列表
        """

        return [i for i in self.elements if type(i) is element_type]

    def has(self, element_type: MessageElement) -> bool:
        return element_type in [type(i) for i in self.elements]

    @staticmethod
    def fromJsonList(obj_list: List) -> 'MessageChain':
        """根据消息的json数据生成MessageChain,主要用于websocket的on_message事件"""

        list = []
        for obj in obj_list:
            try:
                if obj['type'] in ['Source', 'Plain', 'Image', 'At', 'AtAll', 'App', 'Xml']:
                    list.append(
                        getattr(eval(obj['type']), 'fromJson')(obj))
                    # 生成对应Type的MessageElement
            except:
                print('unknow message')
                print(obj)
                continue
        return MessageChain(list)

    def __iter__(self):
        return iter(self.elements)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.elements[key]
        elif isinstance(self, slice):
            return self.__class__(self.elements[key])
        elif issubclass(key, MessageElement):
            return self.get(key)
        else:
            raise NotImplementedError
