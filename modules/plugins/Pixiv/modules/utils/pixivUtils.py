
from pixivpy3 import *
from modules.conf import config
import datetime


class PixivUtils:
    def __init__(self) -> None:
        self.app = AppPixivAPI()
        # self.app = ByPassSniApi()
        # self.app.require_appapi_hosts(hostname="public-api.secure.pixiv.net")
        self.app.auth(refresh_token=config.getPixivConf(option='refreshToken'))

    def getRanking(self, mode: str, date: datetime.date = None, offset=None):
        """id,title,url,tag,user,author,date"""
        json_result = self.app.illust_ranking(mode=mode, date=date, offset=offset)
        return [tuple((
                illust.id,
                illust.title,
                illust.meta_single_page.get('original_image_url', illust.image_urls.large),
                ' , '.join([t.name for t in illust.tags]),
                illust.user.id,
                illust.user.name,
                date.strftime('%y-%m-%d'),
                )) for illust in json_result.illusts]

    def getUserIsvalid(self, user: int) -> bool:
        json_result = self.app.user_detail(user)
        if 'error' in json_result:
            return False
        return True

    def getUserPic(self, user: int, offset=None):
        json_result = self.app.user_illusts(user_id=user, offset=offset)
        return [tuple((
                illust.id,
                illust.title,
                illust.meta_single_page.get('original_image_url', illust.image_urls.large),
                ' , '.join([t.name for t in illust.tags]),
                illust.user.id,
                illust.user.name,
                illust.create_date[:10],
                )) for illust in json_result.illusts if illust.sanity_level < 6] #打开R-18开关后需要过滤一下

    def downImg(self, url: str, path: str, name=None) -> bool:
        #  referer="https://www.pixiv.net/"
        return self.app.download(url=url, path=path, name=name)
