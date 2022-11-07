# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from datetime import datetime
from datetime import timedelta

class ChooseWeekendTides:
    weeknames = ["Momdag", "Diemstag", "Mettwoch", "Dundurstag", "FREYTAG", "Samsday", "Sonnday"]
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        day = adapter.get('day')
        if(day.isoweekday() > 5):
            return item
        else:
            raise DropItem(f"{self.weeknames[day.weekday()]} as it is not a Weekend-day")


from caldav import DAVClient
from caldav import error

class InsertIntoCalDav:
    def __init__(self, base_url, calendar, user, password):
        print("Trying it with " + user + " and " + password)
        self.client = DAVClient(
            username=user,
            password=password,
            url=base_url
        )
        self.calendar = calendar
        self.principal = self.client.principal()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            base_url = crawler.settings.get('CALENDAR_BASE_URL'),
            calendar = crawler.settings.get('CALENDAR_NAME'),
            user = crawler.settings.get('CALENDAR_USER'),
            password = crawler.settings.get('CALENDAR_PASS'),
        )

    def open_spider(self, spider):
        # init
        yield

    def close_spider(self, spider):
        #close
        yield

    def process_item(self, item, spider):
        # save it
        return item
