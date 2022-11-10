import scrapy
import datetime

def most_frequent(List):
    return max(set(List), key = List.count)

class TideForecastSpider(scrapy.Spider):
    name = 'tide-forecast'
    allowed_domains = ['tide-forecast.com']

    def start_requests(self):
        if not hasattr(self, "location") or not self.location:
            print ("location not given. pass '-a location=somewhere,somewhere_else'")
            raise BaseException

        for location in self.location.split(","):
            yield scrapy.Request(f'https://www.tide-forecast.com/locations/{location}/tides/latest')

    def parse(self, response):
        location = response.css('.tide-header__title::text').get().split("times for ")[-1]

        windspeeds_raw = [int(elem) for elem in response.css('text.wind-icon__val::text').getall() if elem.isnumeric()]
        windspeed_unit = response.css('.tide-table__label--wind .windu::text').get()
        wind_directions_raw = response.css('div.wind-icon__tooltip::text').getall()

        #first day always quad resolution
        fistday_num_samples = 4
        firstday_average_windspeed = sum(windspeeds_raw[:fistday_num_samples])/fistday_num_samples
        firstday_average_direction = most_frequent(wind_directions_raw[:fistday_num_samples])
        windspeeds = windspeeds_raw[fistday_num_samples:]
        #windspeeds.insert(0, firstday_average_windspeed)   # First day is not present in daycards!
        wind_directions = wind_directions_raw[fistday_num_samples:]
        #wind_directions.insert(0, firstday_average_direction)

        daycards = response.css('div.tide-day')
        for day, daycard in enumerate(daycards):
            datetext = daycard.css('.tide-day__date::text').get().split(": ")[-1]
            datetext_format = '%A %d %B %Y'
            thisday_date = datetime.datetime.strptime(datetext, datetext_format)

            sunmooncells = daycard.css('td.tide-day__sun-moon-cell')
            sunrise_text = sunmooncells[0].css('.tide-day__value::text').get()
            sunset_text = sunmooncells[1].css('.tide-day__value::text').get()
            sunrise_date = datetime.datetime.strptime(datetext + " " + sunrise_text, datetext_format + ' %I:%M%p')
            sunset_date = datetime.datetime.strptime(datetext + " " + sunset_text, datetext_format + ' %I:%M%p')  

            rows = daycard.css('tr')
            for row in rows:
                elems = daycard.css('td')
                for i, elem in enumerate(elems):
                    text = elem.css('::text').get()
                    if (text == 'Low Tide' or text == 'High Tide'):
                        timetext = elems[i+1].css('::text').get()
                        # fuck america
                        if (timetext.split(":")[0] == "00"):
                            timetext = "12:" + timetext.split(":")[1]
                        height = elems[i+2].css('::text').get()
                        full_time = datetime.datetime.strptime(datetext + " " + timetext, datetext_format + ' %I:%M %p')
                        #print ("Found " + text + " at " + str(full_time) + " (" + height + ")")
                        yield({
                            'time' : full_time,
                            'isFlut': text == 'High Tide',
                            'height_text' : height,
                            'sunrise' : sunrise_date,
                            'sunset' : sunset_date,
                            'wind_speed' : windspeeds[day] if day < len(windspeeds) else 0,
                            'wind_unit' :  windspeed_unit,
                            'wind_dir' : wind_directions[day] if day < len(wind_directions) else 'Unknown',
                            'location' : location,
                            "data_source" : response._url,
                            "crawl_time" : datetime.datetime.now()
                        })

