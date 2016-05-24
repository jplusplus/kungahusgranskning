# encoding: utf-8

from royal_calendar import RoyalCalendar
from dk import DKCalendar
from no import NOCalendar
from se import SECalendar

""" Example queries to get Danish calendar:
"""
# Init
dk_calendar = DKCalendar("data/calendars.db")    

# Scrape events
data = dk_calendar.scrape_until(2014)

"""
# Add data to db
dk_calendar.insert_by_event_data(data, additional_keys=["link"])

# Add persons related to events
dk_calendar.add_persons_to_events()

# Save to csv
dk_calendar.save_csv()
"""     



""" Example queries to get Norwegian calendar

# Init
no_calendar = NOCalendar("data/calendars.db")

# Scrape data for a number of years
data = no_calendar.scrape([2015,2016])

# Add data to db
no_calendar.insert_by_person_data(data)
"""


"""
# Init
se_calendar = SECalendar("data/calendars.db")

# Scrape data for a number of years
data = se_calendar.scrape([2015,2016])

# Add data to db
se_calendar.insert_by_person_data(data, additional_keys=["title"])
"""


""" General calendar functions.
"""
"""
# Init
calendar = RoyalCalendar("data/calendars.db")

# Sync "by event" and "by person" tables
calendar.sync_tables()

# Save tables to csv
calendar.save_csv()
"""