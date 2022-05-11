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

目前插件位于`/modules/plugins`,`/modules/schedule`,`/modules/events`,分别对应一般的消息插件,定时 or 轮询插件,mirai 事件插件(如新人入群,禁言等).
不需要的插件也可以直接删除,插件的用法直接看对应插件代码内说明,以下路径省略了`/modules`

| 名称               |      功能      |                   位置                   |                                               备注                                               |
|------------------|:------------:|:--------------------------------------:|:----------------------------------------------------------------------------------------------:|
| Control          |  功能控制器(群内)   |           `/plugins/Control`           |                                               无                                                |
| Genshin          |      原神      | `/plugins/Genshin`,`/schedule/Genshin` |                                     签到,查询信息,私聊bot绑定cookie                                      |
| Sign             |      签到      |            `/plugins/Sign`             |                                        抽签并给1张彩票和500游戏币                                         |
| Announcement     |      群发      |        `/plugins/Announcement`         |                                               无                                                |
| ExchangeRate     |     汇率转换     |        `/plugins/ExchangeRate`         |                              [申请fixer的apiKey](https://fixer.io/)                               |
| JDPrice          |   JD商品价格监控   | `/plugins/JDPrice`,`schedule/JDPrice`  |                                               无                                                |
| KeywordDetection |  屏蔽关键词(含图片)  |      `/plugins/KeywordDetection`       |                   [申请百度ocr的api](https://cloud.baidu.com/product/ocr_general)                   |
| Lolicon          | 色图插件(不含18X)  |           `/plugins/Lolicon`           |                       [申请lolicon的apiKey](https://api.lolicon.app/#/setu)                       |
| Lottery          |      彩票      | `/plugins/Lottery`,`/schedule/Lottery` |                                            分买票和定时开奖                                            |
| MusicShare       |   点歌(网易云)    |         `/plugins/MusicShare`          |                                               无                                                |
| MyIP             | 返回 bot 当前 IP |            `/plugins/MyIP`             |                                               无                                                |
| Pixiv            | 色图插件(不含18X)  |   `/plugins/Pixiv`,`/schedule/Pixiv`   | 分随机抽图和关注推送,需[获取refreshToken](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362) |
| Remind           |     定时提醒     |  `/plugins/Remind`,`/schedule/Remind`  |                                           分设置提醒和轮询任务                                           |
| Rss              |   订阅Rsshub   |     `/plugins/Rss`,`/schedule/Rss`     |                               分订阅和轮询任务,需自建rsshub(启用Access_Token)                               |
| Translation      |      翻译      |         `/plugins/Translation`         |                           [申请百度翻译api](https://fanyi-api.baidu.com/)                            |
| UrlThumb         |      快览      |          `/plugins/Urlthumb`           |                 url地址快览,其中B站视频解析抄自[ABot](https://github.com/djkcyl/ABot-Graia)                 |
| Weather          |     天气查询     |           `/plugins/Weather`           |                             [申请和风天气api](https://www.qweather.com/)                             |
| XHDict           |     查字典      |           `/plugins/XHDict`            |            服务器需安装playwright的chromium,抄自[ABot](https://github.com/djkcyl/ABot-Graia)            |
| NCOV             |     疫情查询     |            `/plugins/NCov`             |         API引用[DXY-COVID-19-Crawler](https://github.com/BlankerL/DXY-COVID-19-Crawler)          |
| Newspaper        |    60s早报     |         `/schedule/Newspaper`          |                                               无                                                |
| Calendar         |    摸鱼人日历     |          `/schedule/Calendar`          |                                               无                                                |
| CardChange       |   群员昵称改变触发   |          `/events/CardChange`          |                                               无                                                |
| MemberMute       |   群员被禁言触发    |          `/events/MemberMute`          |                                               无                                                |
| Welcome          |    新人入群触发    |           `/events/Welcome`            |                                               无                                                |

## 致谢

特别感谢[JetBrains](https://www.jetbrains.com/)提供的免费开源License：https://jb.gg/OpenSourceSupport

[<img width="150" src="modules/resource/img/logo/jb_beam.png">](https://jb.gg/OpenSourceSupport)










