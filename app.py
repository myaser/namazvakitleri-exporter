#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from ics import Calendar, Event
from ics.alarm import AudioAlarm, DisplayAlarm
from ics.grammar.parse import ContentLine
from sanic import Sanic
from sanic.config import SANIC_PREFIX
from sanic.response import stream, text
from sanic.views import HTTPMethodView
import pytz

DEFAULT_PRAYER_TIMES_BASE_URL = 'http://namazvakitleri.diyanet.gov.tr/en-US/'


class PrayerTimesView(HTTPMethodView):

    def _html_to_ics(self, markup: str, timezone: pytz.timezone) -> Calendar:
        soup = BeautifulSoup(markup, "lxml")
        monthly_prayers = soup.find("div", {"id": "tab-1"}).table
        headers = [i.text for i in monthly_prayers.thead.tr.find_all('th')][1:]
        data = [
            [i.text for i in tr.find_all('td')]
            for tr in monthly_prayers.tbody.find_all('tr')
        ]
        calendar = Calendar(creator=app.config['APPLICATION_ID'])
        for day_record in data:
            events_starts = [
                timezone.localize(datetime.strptime(day_record[0] + ' ' + _time, '%d.%m.%Y %H:%M')) for _time in
                day_record[1:]
            ]
            for i in range(len(headers)):
                display_alarm = DisplayAlarm(trigger=events_starts[i], display_text=headers[i])
                audio_alarm = AudioAlarm(trigger=events_starts[i])
                audio_alarm.sound = ContentLine(
                    'ATTACH', {'FMTTYPE': ['audio/mpeg']},
                    app.config['ADHAN_AUDIO']
                )

                calendar.events.add(
                    Event(name=headers[i], begin=events_starts[i], duration=timedelta(minutes=1),
                          alarms=[audio_alarm, display_alarm])
                )
        return calendar

    async def get(self, request, city_id):
        url = urljoin(app.config['PRAYER_TIMES_BASE_URL'], city_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                markup = await response.text()
        try:
            timezone = pytz.timezone(request.args.get('tz', 'UTC'))
        except pytz.UnknownTimeZoneError:
            return text("error: unknown time zone\n", status=400)
        calendar = self._html_to_ics(markup, timezone=timezone)

        async def stream_calendar(response):
            for line in calendar:
                await response.write(line)

        return stream(
            stream_calendar, content_type='text/calendar',
            headers={'Content-disposition': 'filename="calendar.ics"'}
        )


class Settings:
    PRAYER_TIMES_BASE_URL = 'http://namazvakitleri.diyanet.gov.tr/en-US/'
    APPLICATION_ID = 'https://git.io/Jf0To'
    ADHAN_AUDIO = 'https://ia800804.us.archive.org/8/items/adhan_201709/adhan1.mp3'


app = Sanic("prayer times to ical")
app.config.from_object(Settings)
app.config.load_environment_vars(prefix=SANIC_PREFIX)

app.add_route(PrayerTimesView.as_view(), '/<city_id:string>')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get('PORT', 8000), access_log=True)
