from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import dataset
import requests
import re
import pdb
from royal_calendar import RoyalCalendar

class DKCalendar(RoyalCalendar):
    def _open_calendar(self):
        """ Make driver open calendar and switch to list view
        """
        print("Open calendar")
        self.driver.get(self.start_url)
        self.driver.find_element_by_class_name("switch-to-calendar-list").click()

    def _parse_date(self, datetime_string):
        """ Parse a datetime object from a Danish date string
            Example: MANDAG 02. NOVEMBER 2015 | KL. 10:00
            TODO: include time of day
        """
        MONTHS = ["januar","februar","marts", "april","maj","juni","juli","august","september","oktober","november","december"]
        datetime_list = datetime_string.split("|")
        date_string = datetime_list[0].lower()
        time_string = datetime_list[1].lower()
        date_components = re.search(r"(\d{1,2}). ([a-z]{1,20}) (\d{4})", date_string)
        year = int(float(date_components.group(3)))
        month = MONTHS.index(date_components.group(2)) + 1
        day = int(float(date_components.group(1)))
        return datetime(year,month,day)


    def _parse_calender(self):
        """ Parse events as a list of dicts from the current calendar view.
        """
        print("Parse current calendar view")
        html = self.driver.find_element_by_tag_name("html").get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')
        rows =  soup\
            .find("div", {"class": "pane-event-month"})\
            .find_all("div", class_="views-row")

        data = []
        for row in rows:
            date_string = row\
                .find("span", {"class":"date-display-single"})\
                .text

            data.append({
                "link": row.find("a")["href"],
                "description": row.find("a").text,
                "date": self._parse_date(date_string),
                "country": "Danmark"
            })
        return data

    def _go_to_previous_month(self):
        """ Make driver open previous month
        """
        print("Go to previous month")
        self.driver.find_elements_by_class_name("date-prev")[-1]\
            .find_element_by_tag_name("a")\
            .click()

    def get_current_year_and_month(self):
        """ Get the year and month of the current driver view.
        """
        heading = self.driver.find_elements_by_xpath("//div[@class='date-heading']/h3")[-1].text
        year = float(int(heading.split(" ")[1]))
        month = heading.split(" ")[0]

        return { "year": year, "month": month }

    def scrape_until(self, year):
        """ Scrape all calender events from today until a given year.
            Returns data as a list of dicts.
        """
        self.driver = webdriver.Firefox()
        self.start_url = "http://kongehuset.dk/menu/kalender"

        # Get a list of all persons
        self._open_calendar()

        data = []
        current_date = self.get_current_year_and_month()
        while current_date["year"] > year:
            print ("Parse %s, %s" % (current_date["month"], current_date["year"]))
            month_data = self._parse_calender()
            data += month_data
            sleep(1)
            self._go_to_previous_month()
            current_date = self.get_current_year_and_month()

        self.data = data
        return data


    def add_persons_to_events(self, update_all=False):
        """ To get the persons related to an event we have to
            open the event page and scrape the list of related
            persons.
            This functions updates the database with by attaching
            related persons to each event.
            Set update_all=True to force an update of all events
            in database.
        """
        if update_all:
            events = self.db_table.all()
        else:
            events = self.db_table.find(persons='')

        for row in events:
            url = "http://kongehuset.dk%s" % row["link"]
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            persons = []
            for item in soup.find_all("h6"):
                """ The list of "related items" can include both
                    persons and events etc. Exclude the latter. 
                """
                if "/den-kongelige-familie/" in item.find("a")["href"]:
                    persons.append(item.find("a").text.strip())

            row["persons"] = ",".join(persons)
            print ("Found following persons: " + row["persons"])
            self.db_table.upsert(row, ["link"])



