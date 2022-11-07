import scrapy
import datetime

class TideForecastSpider(scrapy.Spider):
    name = 'tide-forecast_extractor'
    start_urls = ['https://www.tide-forecast.com/locations/Robbensudsteert-Germany/tides/latest']
    
    def parse(self, response):
        daycards = response.css('div.tide-day')
        for daycard in daycards:
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
                        yield({'time' : full_time, 'isFlut': text == 'High Tide', 'height_text' : height, 'sunrise' : sunrise_date, 'sunset' : sunset_date})

