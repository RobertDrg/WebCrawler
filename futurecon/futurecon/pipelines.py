# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import sqlite3


class FutureconPipeline:
    def __init__(self):
        self.con = sqlite3.connect("futurecon.db")
        self.cursor = self.con.cursor()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS events(
        event_title)""")

    def process_item(self, item, spider):
        return item
