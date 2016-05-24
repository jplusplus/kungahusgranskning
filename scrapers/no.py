import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pdb
from royal_calendar import RoyalCalendar

class NOCalendar(RoyalCalendar):
    def _get_persons(self):
        """ Get a list of the royal persons in Norway
        """
        if not hasattr(self, 'persons'):
            url = "http://www.kongehuset.no/program.html?tid=27511&sek=26946"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            options = soup.find("select", { "name": "person" })\
                .find_all("option")
            self.persons = zip(
                [x.text for x in options],
                [x["value"] for x in options]
            )
        return self.persons[2:]
    
    def _parse_text(self, element):
        """ Get text of element, return None if empty
        """
        try:
            return element.text
        except AttributeError:
            return None

    def _parse_date(self, date_string):
        """ Parse a date string to datetime object
            Example: 14.01.2016
        """

        date_string = date_string.split("-")
        date_start_list = [int(float(x)) for x in date_string[0].split(".")]
        date_start = datetime(date_start_list[2],date_start_list[1],date_start_list[0])
        if len(date_string) > 1:
            date_end_list = [int(float(x)) for x in date_string[1].split(".")]
            date_end = datetime(date_end_list[2],date_end_list[1],date_end_list[0])
        else:
            date_end = None

        return {
            "start": date_start,
            "end": date_end
        }


    def _parse_events(self, html):
        """ Get all events from a calender view (as html) and
            return a list of dicts.
        """
        print "Parse events"
        data = []
        soup = BeautifulSoup(html, "html.parser")
        events = soup.find_all("div", {"class": "program clearfix"})
        """ Site's html is broken. We have to handle descriptions 
            with a hack.
        """
        descriptions = soup.find_all("div", {"class": "programpostingress"})
        for index, event in enumerate(events):
            link_tag = event.find("a")
            if link_tag:
                link = link_tag["href"]
            else:
                link = None
            dates = self._parse_date(self._parse_text(event.find("span", {"class": "programpostdato"})))
            row = {
                "title": self._parse_text(event.find("span", {"class": "programposttittel"})),
                "date_start": dates["start"],
                "date_end": dates["end"],
                "description": self._parse_text(descriptions[index]),
                "link": link,
                "country": "Norge"
            }
            data.append(row)
        print "Found %s events" % len(data)
        return data

    def scrape(self, years=[2016]):
        """ Scrape events for a list of years.
            Returns a list of dicts. 
        """
        data = []
        for person in self._get_persons():
            for year in years:
                person_id = person[1]
                url = "http://www.kongehuset.no/programarkiv.html?tid=30387&sek=30041&person=%s&ar=%s" % (person_id, year)
                print("Scrape %s" % url)
                r = requests.get(url)
                person_data = self._parse_events(r.text)
                for row in person_data:
                    row["person"] = person[0]
                    row["url"] = url
                data += person_data

        return data

