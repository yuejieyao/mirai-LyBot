# private-mirai-plugins
![image](https://img.shields.io/badge/python-3.7+-green.svg)

自用的 mirai 插件,在框架上大量参考了 [Graia Project](https://github.com/GraiaProject/Application),由于graia暂时还未迁移到 2.0+版本的 mirai_http_api 上,所以自己仿着写了一个简版的,还有很多功能没做,代码也比较乱

## 安装依赖包

```
  pip install -r requirements.txt
```

## 使用

```
  python main.py
```

## 说明

所有的功能都作为插件方式存在于`/modules/plugins`,不需要直接删对应的插件即可
要使用的话需要在 config.conf 中配置对应的 api 信息
当前功能
| 插件 | 功能 | 需要 |
| ---------- | :-----------: | :-----------: |
| Announcement | 公告(群发,并不是群公告) | 无 |
| ExchangeRate | 汇率转换 | [fixer(可能有墙)](https://fixer.io/) |
| KeywordDetection | 屏蔽关键词 | [百度 ocr 文字识别 api](https://cloud.baidu.com/product/ocr_general) |
| Lolicon | 色图插件 | [lolicon](https://api.lolicon.app/#/setu) |
| MusicShare | 点歌(网易云) | 无 |
| Translation | 翻译 | [百度翻译开放平台](https://fanyi-api.baidu.com/) |
| UrlThumb | 快览 | (可能有墙) |
