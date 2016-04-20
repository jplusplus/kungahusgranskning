# encoding: utf-8

from dk import DKCalendar

dk_calendar = DKCalendar("data/calendars.db")
#data = dk_calendar.scrape_until(2014)
#dk_calendar.insert_data(data, additional_keys=["link"])
#dk_calendar.add_persons_to_events()
dk_calendar.save_csv()