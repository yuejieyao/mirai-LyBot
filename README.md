# mirai-LyBot

![image](https://img.shields.io/badge/python-3.7+-green.svg)

基于 [mirai](https://github.com/mamoe/mirai) 和 [mirai-api-http](https://github.com/project-mirai/mirai-api-http)

## 安装依赖包

```
  pip install -r requirements.txt
```

## 使用

```
  python main.py
```

## 说明

功能插件位于`/modules/plugins`,不需要可以直接删对应的插件,使用前需在 config.conf 中配置对应的 api 信息

定时任务插件位于`/modules/schedule`,不需要可以直接删对应的插件

当前完成的功能
| 插件 | 功能 | 需要 |
| ---------- | :-----------: | :-----------: |
| Control | 插件控制器(暂时只写了群里的) | 无 |
| Sign | 签到(抽签) | 无 |
| Announcement | 公告(群发,并不是群公告) | 无 |
| MyIP | 返回 bot 当前 IP | 无 |
| ExchangeRate | 汇率转换 | [fixer(可能有墙)](https://fixer.io/) |
| KeywordDetection | 屏蔽关键词(含图片) | [百度 ocr 文字识别](https://cloud.baidu.com/product/ocr_general) |
| Lolicon | 色图插件(不含 18X) | [lolicon](https://api.lolicon.app/#/setu) |
| Pixiv | 色图插件(不含 18X) | [自行获取 refreshToken](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362) |
| MusicShare | 点歌(网易云) | 无 |
| Translation | 翻译 | [百度翻译开放平台](https://fanyi-api.baidu.com/) |
| UrlThumb | 快览 | (可能有墙) |
| Weather | 天气查询 | [和风天气](https://www.qweather.com/) |
| Today | 历史上的今天(定时任务) | 无 |
| Rss | 订阅 Rsshub | 自建 rsshub(启用 Access_Token) |
| XHDict | 查字典 | 安装playwright的chromium |
| Newspaper | 60s早报(定时任务) | 无 |
| Remind | 定时提醒 | 无 |