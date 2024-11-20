# coding=utf-8

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import time

from items import FileDownloadItem
from database import Database
from pipelines.folder_path import get_app_folder
from settings import DEFAULT_CATEGORY, DEFAULT_SIZE, DEFAULT_VERSION


class ContentPipelineFjc(object):

    def __init__(self):
        """
        init func
        """
        # init database source
        # self.db_handler = Database()

    def process_item(self, item: FileDownloadItem, spider):
        # item.setdefault("file_urls", "https://apkpure.com/party-mini-games-play-offline/com.missingames.arcade/downloading/2.0.0.4")
        # app_folder = get_app_folder(item)
        # if not os.path.exists(app_folder):
        #     os.makedirs(app_folder)

        # 保存app介绍
        # if item['description']:
        #     des_file = os.path.join(app_folder, "description.txt")
        #     with open(des_file, 'w') as _file_:
        #         _file_.write(item["description"])

        # 保存app和update信息
        # self.db_handler.insert_app(item)
        print("item:", item)
        return item
