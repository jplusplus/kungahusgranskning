# encoding: utf-8
"""Categorize events according to where they took place
"""

from modules.interface import Interface
from csvkit import DictReader
from modules import palaces


def get_location_category(text):
    """Use all available method, return first match"""
    try:
        if palaces.contains_palace_name(text):
            return palaces.AT_HOME
    except palaces.NotFoundError:
        pass
#    try:
#        return palaces.contains_palace_name(text)
#    except palaces.NotFoundError:
#        pass

    return palaces.UNKNOWN


def main():
    """ Entry point when run from command line
    """
    # pylint: disable=C0103

    cmd_args = [{
        'short': "-i", "long": "--infile",
        'dest': "infile",
        'type': str,
        'help': """CSV file with calendar data""",
        'required': True
    }]
    ui = Interface("BlockePlaces",
                   "Find out where events took place",
                   commandline_args=cmd_args)
    ui.info(ui.args.infile)

    with open(ui.args.infile) as infile:
        csv_reader = DictReader(infile)
        places = {}
        for row in csv_reader:

            location_category = get_location_category(row["title"])
            if location_category == palaces.UNKNOWN:
                location_category = get_location_category(row["description"])

            person = row["person"]
            if person not in places:
                places[person] = {
                    palaces.UNKNOWN: 0,
                    palaces.AT_HOME: 0,
                    palaces.DOMESTIC: 0,
                    palaces.ABROAD: 0
                }
            places[person][location_category] += 1
        print places

if __name__ == '__main__':
    main()
