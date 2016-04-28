import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pdb
from royal_calendar import RoyalCalendar

MONTHS = ["", "januari", "februari", "mars","april","maj","juni","juli","augusti","september","oktober","november","december"]

class SECalendar(RoyalCalendar):
    def _parse_events(self, person, year):
        """ Get a list of dicts with events for a given person in a given year.
            Will iterate through pagination.
        """
        """ Separating queries by year and person makes it easier to
            relate person and dates to events (years are not printed in 
            the calendar for example).
        """
        data = []
        page = 1
        start_date = "%s-01-01" % year
        end_date = "%s-12-31" % year
        has_next_page = True
        while has_next_page:
            url = "http://www.kungahuset.se/kalender.4.7c4768101a4e888378000228.html?deltagare=%s&kalender_startdatum=%s&kalender_slutdatum=%s&page=%s" % (person, start_date, end_date, page)
            print "Scrape %s" % url
            r = requests.get(url)

            soup = BeautifulSoup(r.text, "html.parser")
            events = soup.find_all("div", { "class": "lp-article"})
            print "Found %s events" % len(events) 
            for event in events:
                day = int(float(event.find("span", { "class": "lp-day" }).text))
                month_name = event.find("span", { "class": "lp-month" }).text.lower()
                month = MONTHS.index(month_name)
                row = {}
                row["date_start"] = datetime(year,month,day)
                row["date_end"] = None
                row["title"] = event.find("h2").text
                row["country"] = "Sverige"
                row["person"] = person

                """ Event details such as "plats" and "kontakt" are 
                    defined in a somewhat loose html format.
                """
                details = event.find_all("p")[-1].decode_contents(formatter="html").split("<br/>")
                for detail in details:
                    if "<strong>Plats:</strong>" in detail:
                        row["location"] = detail.split("</strong>")[-1].strip()
                    
                    link = BeautifulSoup(detail, 'html.parser').find("a")
                    if link:
                        if "mailto" not in link["href"]:
                            row["link"] = link["href"]
                data.append(row)

            try:
                last_page = soup.find("ul",{"class":"lp-pagination"})\
                    .find_all("a", {"class": "lp-page"})[-1]
                has_next_page = page < int(float(last_page.text))
            except AttributeError:
                has_next_page = False

            page += 1

        return data


    def _get_persons(self):
        """ Returns a list of the royal persons in Sweden.
        """
        url = "http://www.kungahuset.se/kalender"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        persons = [x["value"] for x in soup.find('select', {'id': 'deltagare'}).find_all('option')][1:]
        persons.remove("Besöksmålen")
        return persons

    def scrape(self, years=[2016]):
        """ Scrape calendars for events for a list of years.
            Returns a list of dicts.
        """
        data = []
        for year in years:
            for person in self._get_persons():
                person_data= self._parse_events(person, year)
                data += person_data

        return data