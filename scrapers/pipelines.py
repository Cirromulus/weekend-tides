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
        self.calendar_id = calendar
        self.principal = self.client.principal()
        self.margin = timedelta(minutes=60)
        self.use_expanded_search = True

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            base_url = crawler.settings.get('CALENDAR_BASE_URL'),
            calendar = crawler.settings.get('CALENDAR_NAME'),
            user = crawler.settings.get('CALENDAR_USER'),
            password = crawler.settings.get('CALENDAR_PASS'),
        )

    def open_spider(self, spider):
        self.calendar = self.principal.calendar(cal_id=self.calendar_id)
        assert self.calendar
        print("Opening " + self.calendar.get_display_name())
        
        try:
            events_fetched = self.calendar.date_search(
                start=datetime.now(), end=datetime.now()+self.margin, expand=True
            )
        except:
            self.use_expanded_search = False
        
    def close_spider(self, spider):
        #close
        yield

    def process_item(self, item, spider):
        # save it
        adapter = ItemAdapter(item)
        time = adapter.get('time')
        
        for conflicting_element in self.calendar.date_search(
                start=time - self.margin*2,
                end=time + self.margin*2,
                expand=self.use_expanded_search
            ):
            print("Deleting conflicting event " + str(conflicting_element))
            conflicting_element.delete()

        title = "Hochwasser"
        desc = ""
        if adapter.get('wind_speed') > 0:
            title += " bei "
            value = adapter.get('wind_speed')
            unit = adapter.get('wind_unit')
            if adapter.get('wind_unit') == "km/h":
                value *= 0.539957
                unit = "knots"
            else:
                print("Unknown speed unit " + adapter.get('wind_unit') + "!")
            title += str(round(value)) + " " + unit + " " + adapter.get('wind_dir')
        else:
            title += " um " + time.strftime("%H:%M")
            desc += "Windgeschwindigkeit noch nicht bekannt.\n"

        desc += "Hochwasser bei " + adapter.get('height_text') + "\n"
        desc += "\nStand " + adapter.get('crawl_time').strftime("%Y-%m-%d") + ", Quelle: " + adapter.get('data_source') + "\n"
        desc += "\n" + str(item)

        kite_event = self.calendar.save_event(
            dtstart = time - self.margin,
            dtend = time + self.margin,
            summary = title,
            description = desc
        )
        return item







