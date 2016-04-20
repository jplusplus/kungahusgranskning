# encode: utf-8
import dataset

class RoyalCalendar(object):
    def insert_data(self, data, additional_keys=[]):
        """ Pass a list of dicts and update database.
            Some calendar events need additional keys to identify unique
            events (eg a link) if there are multiple events on the same 
            day. 
        """
        print ("Add %s rows to database" % len(data))
        keys=["date", "country"] + additional_keys
        for row in data:
            self.db_table.upsert(row, keys)

    def save_csv(self, filename="data/calendar.csv"):
        """ Save calendar as csv
        """
        print "Save event database as %s" % filename
        dataset.freeze(self.db_table.all(), format='csv', filename=filename)

    def __init__(self, db_path):
        db = dataset.connect('sqlite:///%s' % db_path)
        self.db_table = db["events"]