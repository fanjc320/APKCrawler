# -*- coding: utf-8 -*-
import logging
import random

import settings
from scrapy.http import HtmlResponse
class UserAgentMiddleware:
    logger = logging.getLogger("User Agent Middleware")

    def process_request(self, request, spider):
        random_ua = random.choice(settings.USER_AGENT_LIST)
        request.headers['User-Agent'] = random_ua
        # if spider.settings["USING_PROXY"]:
        #     request.meta['proxy'] = settings.PROXY_PATH



class CloudScraperMiddleware:
    def process_response(self, request, response, spider):
        if response.status == 403:
            print("middleware 403!!!!!!!!")
            url = request.url
            req = spider.scraper.get(url, headers={'referer': url})
            return HtmlResponse(url=url, body=req.text, encoding="utf-8", request=request)
        return response