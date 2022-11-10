Simple Project to get schedule kite-able days into your CalDav Calendars.

Using weekend-tides
===================

1. Insert your CalDav credentials by `cp env-example .env` and editing the created file.
2. Install requirements using `pip install -r requirements.txt`
3. Run one of the available spiders under `scrapers/spiders/*.py` by calling `scraply crawl [name] -a location=here,there`, e.g. `scrapyl crawl tide-forecast_extractor -a location=Robbensudsteert-Germany,Schillig-Germany`.

