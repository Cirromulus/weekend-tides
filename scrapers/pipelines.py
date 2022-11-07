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
        day = adapter.get('time')
        if(day.isoweekday() > 5):
            return item
        else:
            raise DropItem(f"{self.weeknames[day.weekday()]} as it is not a Weekend-day")

class ChooseHighTidesWithDaylight:
    def __init__(self):
        self.margin = timedelta(minutes=60)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        sunrise = adapter.get('sunrise') + self.margin
        sunset = adapter.get('sunset') - self.margin
        if adapter.get('isFlut'):
            if sunrise <= adapter.get('time') <= sunset:
                return item
        raise DropItem("No high tide within " + str(self.margin) + " of daylight")


class RemoveDuplicates:
    def __init__(self):
        self.unique_data = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('time') not in self.unique_data:
            self.unique_data.add(adapter.get('time'))
            return item
        raise DropItem("Duplicate time")


from caldav import DAVClient
from caldav import error
from caldav import Event

class InsertIntoCalDav:
    def __init__(self, base_url, calendar, user, password):
        #print("Trying CalDav connection with " + user + " and " + password)
        self.client = DAVClient(
            username=user,
            password=password,
            url=base_url
        )
        self.principal = self.client.principal()
        self.calendar = self.principal.calendar(cal_id=calendar)
        self.margin = timedelta(minutes=60)
        print("Opening " + self.calendar.get_display_name())

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            base_url = crawler.settings.get('CALENDAR_BASE_URL'),
            calendar = crawler.settings.get('CALENDAR_NAME'),
            user = crawler.settings.get('CALENDAR_USER'),
            password = crawler.settings.get('CALENDAR_PASS'),
        )

    def open_spider(self, spider):
        #events = self.calendar.events()
        #for event in events:
            #print("not Deleting maybe conflicting event " + str(conflicting_event))
            #conflicting_event.delete()
        yield

    def close_spider(self, spider):
        #close
        yield

    def process_item(self, item, spider):
        # save it
        adapter = ItemAdapter(item)
        time = adapter.get('time')

        kite_event = self.calendar.save_event(
            dtstart = time - self.margin,
            dtend = time + self.margin,
            summary = "Hochwasser bei " + adapter.get('height_text'),
            description = "Wind: Unbekannt.\n" + str(item)
        )
        return item







