# coding=utf-8
import logging
import os
import scrapy
from collections import defaultdict
import requests
from urllib.parse import urlencode
from codes.apks.items import FileDownloadItem
from codes.apks import settings
import cloudscraper

class ApkPureSpider(scrapy.Spider):
    name = "apkpure"
    allowed_domains = ["apkpure.com"]
    logger = logging.getLogger("GoogleSpider")
    custom_settings = {
        "HTTPERROR_ALLOWED_CODES": [403],
        "DOWNLOADER_MIDDLEWARES": {
            # "codes.apks.download_handler.DownloaderMiddleware": 200,
            "codes.apks.download_handler.download_handler.DownloaderMiddleware": 200,
        },
        # "DOWNLOAD_HANDLERS": {
        #     "http": "codes.apks.download_handler.CloudFlareDownloadHandler",
        #     "https": "codes.apks.download_handler.CloudFlareDownloadHandler",
        # }
    }

    def __init__(self):
        super().__init__()
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        # self.url = 'https://xxxx/xxx/xxx/'
        self.proxies = {
            "http": "http://127.0.0.1:10819",
            "https": "http://127.0.0.1:10819",
        }
    def start_requests(self):
        # # 以下对python代理的测试，都是ok的
        # # proxies = {'http': 'http://127.0.0.1:10819/'}
        # # # proxies = {'socket5': 'http://127.0.0.1:10818/'}
        # # r = requests.get("https://www.google.com")#ok
        # # print("testGoogle: r.code:", r.status_code, " r.text:", r.text)
        # # print("testGoogle:",requests.get("https://www.google.com", proxies=proxies).text)
        # # ra = requests.get("https://apkpure.com/app")# 403
        # # print("testApkpure: ra.code:", ra.status_code, " ra.text:", ra.text)
        # # print("testApkpure:",requests.get("https://apkpure.com/app", proxies=proxies).text)
        #
        # start_url = "https://apkpure.com/app"
        # # yield scrapy.Request(start_url, callback=self.parse_diff_cate)
        # scraper = cloudscraper.create_scraper()
        # resp = scraper.get(start_url)
        # yield resp
        # # yield scrapy.Request(start_url, callback=self.parse_diff_cate, meta={'proxy':"socket5://127.0.0.1:10818"})
        # # # yield scrapy.Request(start_url, callback=self.parse_diff_cate, meta={'proxy':"http://127.0.0.1:10819"})

        yield scrapy.Request(
            # url="https://apkpure.com/cn/shawarma-legend/com.company.shaw/download",
            # url="https://apkpure.com/app",
            # url="https://apkpure.com/pre-register",
            url="https://apkpure.com/game_casual",
            headers=self.headers,
            callback=self.parse_diff_cate,
            dont_filter=True,
            meta={"proxies": self.proxies}
        )

    def parse_diff_cate(self, response):
        """
        parse different category
        """
        # print("parse_diff_cate response.body:" + response.text)
        # return

        # categories = response.css("ul.index-category.cicon li a::attr('href')").getall()
        # categories = response.css("body > main > div.category-apk-list-box.category-module.is-tab.dt-newest-sort.dt-sort-box > div.tab-items > div:nth-child(1) > div.apk-grid-item.no-grid.disable-stars-0 > ul > li > div > a").getall()
        # categories = response.css("body > main > div.category-apk-list-box.category-module.is-tab.dt-newest-sort.dt-sort-box   div a::attr(href)").extract_first()
        # categories = response.css("body > main > div.category-apk-list-box.category-module.is-tab.dt-newest-sort.dt-sort-box   div a.grid-item-title::attr(href)").extract() # 可以拿到apk url
        categories = response.css("div.category-apk-list-box.category-multiple-apk-list-box.category-module.is-tab a.grid-item-title::attr(href)").extract() # 可以拿到apk url
        print("---------------------------------------------------------------" + "|||")
        if not categories:
            print("categories is none")
        else:
            # print("categories:" + categories)
            print(categories)
        # print("categories :" + len(categories))
        count=1
        for category in categories:
            if count > 1:
                print("break<<<<<<<<<")
                break
            category_url = response.urljoin(category)
            print("category_url:")
            print(category_url)
            # yield scrapy.Request(category_url, callback=self.parse_app_list)
            count+=1
            # yield scrapy.Request(category_url, callback=self.parse_app)
            yield scrapy.Request(
                category_url,
                headers=self.headers,
                callback=self.parse_app,
                dont_filter=True,
                meta={"proxies": self.proxies}
            )

    def parse_app_list(self, response):
        """
        parse app list
        """
        # 解析应用列表
        app_urls = response.css("ul.category-template#pagedata li div.category-template-img a::attr('href')").getall()
        for app_url in app_urls:
            app_url = response.urljoin(app_url)
            yield scrapy.Request(app_url, callback=self.parse_app)

        # 解析下一页
        next_url = response.css("a.loadmore::attr('href')").get()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse_app_list)

    def parse_app(self, response):
        """
        parse app info page
        """

        # print("response:", response.text)
        # return
        # 解析应用信息
        # app title
        strCss = "div.details.container > div.old-versions.google-anno-skip > div > a:nth-child(3)"
        app_title = response.css(strCss)
        if app_title is None:
            raise ValueError("App Title Error.")

        # # description and update info
        # description = "Description:\n" + "\n".join(response.css("div#describe div.content::text").getall())
        # description += "Update Info:\n" + "\n".join(response.css("div#whatsnew div:nth-child(3)::text").getall())
        #
        # category = response.css("div.additional ul li:first-child a span::text").getall()
        # if len(category) == 0:
        #     raise ValueError("App Type Error.")
        # elif len(category) == 1:
        #     self.logger.info("App '{}' is a paid app. Can't Download it.".format(app_title))
        #     return
        # else:
        #     category = category[1]
        #
        # # latest version
        # latest_version = response.css("div.additional ul li:nth-child(2) p:nth-child(2)::text").get()
        # if not latest_version:
        #     raise ValueError("App Latest Version Error.")
        #
        # # developer
        # publisher = response.css("div.left div.box div.details-author p a::text").get()
        # if not publisher:
        #     raise ValueError("Developer Error.")

        # apk name
        # package_name = os.path.split(response.url)[-1]
        print("app_title:", app_title)
        package_name = response.css(strCss+"::attr(data-dt-package_name)").get()
        print("package_name:", package_name)

        downloadUrl = response.css(strCss+"::attr(href)").get()
        print("downloadUrl:", downloadUrl)
        if not downloadUrl:
            print("downloadUrl is null")
            return

        # file = FileDownloadItem()
        # file['file_urls'] = [downloadUrl]
        # return file

        # app link
        apkpure_url = response.url

        # market
        version = response.css(strCss+"::attr(data-dt-version)").get()
        version_code = response.css(strCss+"::attr(data-dt-version_code)").get()
        print("version:", version)

        yield scrapy.Request(
            downloadUrl,
            headers=self.headers,
            # callback=self.parse_app,
            callback=self.parse_download,
            dont_filter=True,
            meta={"proxies": self.proxies}
        )

        # # picture links
        # picture_links = response.css("div.describe div.describe-img div#slide-box img::attr(src)").getall()
        #
        # app_detail = items.AppDetail(app_title=app_title, apk_name=package_name, description=description, developer=publisher, app_link=apkpure_url, category=category, market=market, version=latest_version, picture_links=picture_links)

        # # 更多版本
        # more_version_url = response.css("div.ver-title div.more a::attr('href')").get()
        # if more_version_url:
        #     more_version_url = response.urljoin(more_version_url)
        #     yield scrapy.Request(more_version_url, meta={"app_detail": app_detail}, callback=self.parse_multi_version)

        # # 相似应用 & 同一厂商
        # more_urls = response.css("div.left div.box div.title div.more a::attr('href')").getall()
        # for more_url in more_urls:
        #     if "similar" in more_url:
        #         # 相似应用
        #         similar_url = response.urljoin(more_url)
        #         yield scrapy.Request(similar_url, callback=self.parse_similar)
        #     elif "developer" in more_url:
        #         # 同一厂商
        #         developer_url = response.urljoin(more_url)
        #         yield scrapy.Request(developer_url, callback=self.parse_developer, meta={"raw_url": apkpure_url})

    # def parse_multi_version(self, response):
    #     """
    #     parse multiple version
    #     """
    #     app_detail = response.meta['app_detail']
    #
    #     ver_lis = response.css("div.ver ul.ver-wrap li")
    #     for ver_li in ver_lis:
    #         version = ver_li.css("a div.ver-item-wrap span.ver-item-n::text").get()[1:]
    #         file_types = ver_li.css("div.ver-item div.ver-item-wrap span.ver-item-t::text").getall()
    #         if "XAPK" in file_types:
    #             file_type = "xapk"
    #         else:
    #             file_type = "apk"
    #         ver_info_dom = ver_li.css("div.ver-info")
    #
    #         if len(ver_info_dom) > 0:  # 没有多个变种
    #             # 获取版本信息
    #             p_doms = ver_info_dom.css("div.ver-info-m p")
    #             page_url = ver_li.css("li>a::attr('href')").get()
    #             page_url = response.urljoin(page_url)
    #             ext_infos = defaultdict(str)
    #             for p_dom in p_doms:
    #                 try:
    #                     _key = p_dom.css("strong::text").get().strip()
    #                 except AttributeError:
    #                     continue
    #
    #                 if _key:
    #                     try:
    #                         _key = _key.split(":")[0].strip()
    #                         _value = p_dom.css("p::text").get().strip()
    #                     except AttributeError as _err:
    #                         continue
    #
    #                     if _key == "Requires Android":
    #                         ext_infos["requirement"] = _value
    #                     elif _key == "Signature":
    #                         ext_infos["signature"] = _value
    #                     elif _key == "Screen DPI":
    #                         ext_infos['dpi'] = _value
    #                     elif _key == "Architecture":
    #                         ext_infos['architecture'] = _value
    #                     elif _key == "Update on":
    #                         ext_infos['update_time'] = _value
    #                     elif _key == "File Size":
    #                         ext_infos['size'] = _value
    #                     elif _key == "File SHA1":
    #                         ext_infos['hash'] = _value
    #             file_size = ext_infos['size'] or settings.DEFAULT_SIZE
    #
    #             update_detail = items.AppDetail(app_title=app_detail['app_title'], apk_name=app_detail['apk_name'], developer=app_detail['developer'], app_link=app_detail['app_link'], category=app_detail['category'], market=app_detail['market'], version="{}.{}".format(version, file_type), size=file_size)
    #
    #             if version == app_detail['version']:
    #                 update_detail['description'] = app_detail['description']
    #                 update_detail['picture_links'] = app_detail['picture_links']
    #             else:
    #                 update_detail['description'] = ""
    #                 update_detail['picture_links'] = []
    #
    #             yield scrapy.Request(page_url, meta={"update_detail": update_detail}, callback=self.parse)
    #         else:  # 存在多个变种
    #             variants_url = ver_li.css("a::attr('href')").get()
    #             variants_url = response.urljoin(variants_url)
    #
    #             yield scrapy.Request(variants_url, meta={"app_detail": app_detail}, callback=self.parse_multi_varia)

    def parse_similar(self, response):
        """
        parse similar apps
        """
        # 解析相似app列表
        similar_apps = response.css("div.main div.box ul#pagedata li dd.title-dd a::attr('href')").getall()
        for similar_app in similar_apps:
            app_url = response.urljoin(similar_app)
            yield scrapy.Request(app_url, callback=self.parse_app)

    def parse_developer(self, response):
        """
        parse the same developer's apps
        """
        # 解析app列表
        devel_apps = response.css("div.main div.left div.box dl.search-dl p.search-title a::attr('href')").getall()
        for devel_app in devel_apps:
            app_url = response.urljoin(devel_app)
            yield scrapy.Request(app_url, callback=self.parse_app)

        # 下一页
        next_page_url = response.css("div.paging ul li:last-child a::attr('href')").get()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(next_page_url, callback=self.parse_developer)

    def parse(self, response, **kwargs):
        """
        parse the download page
        """
        update_detail = response.meta['update_detail']

        # 获取下载地址
        download_url = response.css("div.left div.box div.fast-download-box.fast-bottom p.down-click a::attr('href')").get()
        if not download_url:
            raise ValueError('Get download url Error.')
        update_detail['download_link'] = download_url

        yield update_detail

    # def parse_multi_varia(self, response):
    #     """
    #     parse the multi variants
    #     """
    #     app_detail = response.meta['app_detail']
    #     variants_dom = response.css("div.left div.table div.table-row")[1:]
    #     version = response.css("div.left div.box div.variant div.info div.tit span::text").get()[1:]
    #     app_version_list = []
    #
    #     for variant_dom in variants_dom:
    #         variant_number = variant_dom.css("div.table-cell div.popup span::text").get()
    #
    #         # 解析更新的信息
    #         ver_info_dom = variant_dom.css("div.table-cell div.ver-info div.ver-info-m")
    #         file_type_str = variant_dom.css("div.table-cell.down a::text").get()
    #         if "XAPK" in file_type_str:
    #             file_type = "xapk"
    #         else:
    #             file_type = "apk"
    #         p_doms = ver_info_dom.css("p")
    #         page_url = variant_dom.css("div.table-cell.down a::attr('href')").get()
    #         page_url = response.urljoin(page_url)
    #         ext_info = defaultdict(str)
    #         for p_dom in p_doms:
    #             try:
    #                 _key = p_dom.css("strong::text").get().strip()
    #             except AttributeError:
    #                 continue
    #
    #             if _key:
    #                 _key = _key.split(':')[0].strip()
    #                 _value = _value = p_dom.css("p::text").get().strip()
    #
    #                 if _key == "Update on":
    #                     ext_info['update_time'] = _value
    #                 elif _key == "Requires Android":
    #                     ext_info['requirement'] = _value
    #                 elif _key == "Signature":
    #                     ext_info['signature'] = _value
    #                 elif _key == "Screen DPI":
    #                     ext_info['dpi'] = _value
    #                 elif _key == "Architecture":
    #                     ext_info['architecture'] = _value
    #                 elif _key == "File SHA1":
    #                     ext_info['hash'] = _value
    #                 elif _key == "File Size":
    #                     ext_info['size'] = _value
    #
    #         app_size = ext_info['size'] or settings.DEFAULT_SIZE
    #         architecture = ext_info['architecture'] or settings.DEFAULT_ARCHITECTURE
    #         update_date = ext_info['update_time'] if ext_info['update_time'] != "" else None
    #         app_version = "{}-{}-{}-{}".format(version, variant_number, architecture, file_type)
    #
    #         if app_version in app_version_list:
    #             continue
    #         app_version_list.append(app_version)
    #
    #         update_detail = items.AppDetail(
    #             app_title=app_detail['app_title'], apk_name=app_detail['apk_name'], developer=app_detail['developer'], app_link=app_detail['app_link'], category=app_detail['category'], market=app_detail['market'], version=app_version, size=app_size, update_date=update_date
    #         )
    #         if version == app_detail['version']:
    #             update_detail['description'] = app_detail['description']
    #             update_detail['picture_links'] = app_detail['picture_links']
    #         else:
    #             update_detail['description'] = ""
    #             update_detail['picture_links'] = []
    #
    #         yield scrapy.Request(page_url, meta={"update_detail": update_detail}, callback=self.parse)

    def parse_download(self, response):
        strCss = "div.download-box.download-button-box.google-anno-skip.d-normal.download-button-box-fast-new > a.btn.jump-downloading-btn"
        app_title = response.css(strCss)
        if app_title is None:
            raise ValueError("App Title Error.")

        downloadingUrl = response.css(strCss + "::attr(href)").get()
        name = response.css(strCss + "::attr(title)").get()
        print("parse_download downloadingUrl:", downloadingUrl)
        print("parse_download name:", name)
        # yield scrapy.Request(
        #     downloadUrl,
        #     headers=self.headers,
        #     # callback=self.parse_app,
        #     # callback=self.parse_download,
        #     # callback=self.parse_download,
        #     dont_filter=True,
        #     meta={"proxies": self.proxies}
        # )

        file = FileDownloadItem()
        # file['file_urls'] = [downloadingUrl]
        file['file_urls'] = ["https://apkpure.com/party-mini-games-play-offline/com.missingames.arcade/downloading/2.0.0.4"]
        # file['files'] = [name]
        # file['apk_name'] = [name]
        # file['file_urls'].append(downloadingUrl)

        # file['file_urls'] = ["http://www.nirsoft.net/utils/outlook_nk2_edit.html/nk2edit.zip"]
        return file
