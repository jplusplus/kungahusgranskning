# encode: utf-8
import dataset
from copy import deepcopy

class RoyalCalendar(object):
    def insert_by_event_data(self, data, additional_keys=[]):
        """ Pass a list of dicts and update database.
            Some calendar events need additional keys to identify unique
            events (eg a link) if there are multiple events on the same 
            day. 
        """
        print ("Add %s rows to database" % len(data))
        keys=["date_start", "country"] + additional_keys
        for row in data:
            self.tables["by_event"].upsert(row, keys)

    def insert_by_person_data(self, data, additional_keys=[]):
        print ("Add %s rows to database" % len(data))
        keys = ["date_start", "date_end", "country", "person"] + additional_keys
        for row in data:
            self.tables["by_person"].upsert(row, keys)

    def sync_tables(self):
        by_person_data = []
        for event_row in self.tables["by_event"].all():
            persons = event_row["persons"].split(",")
            base_row = deepcopy(event_row)
            base_row.pop("persons", None)
            base_row.pop("id", None)
            for person in persons:
                person_row = deepcopy(base_row)
                person_row["person"] = person            
                by_person_data.append(person_row)

        self.insert_by_person_data(by_person_data)


    def save_csv(self):
        """ Save calendar as csv
        """
        print "Save event database as csv files"
        dataset.freeze(self.tables["by_event"].all(), format='csv', filename="data/by_event.csv")
        dataset.freeze(self.tables["by_person"].all(), format='csv', filename="data/by_person.csv")

    def __init__(self, db_path):
        db = dataset.connect('sqlite:///%s' % db_path)
        self.tables = {
            "by_event": db["by_event"],
            "by_person": db["by_person"]
        }
        