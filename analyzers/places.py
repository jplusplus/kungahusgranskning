# encoding: utf-8
"""Categorize events according to where they took place
"""

from modules.interface import Interface
from csvkit import DictReader, DictWriter
from modules import palaces


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

    output = []
    with open(ui.args.infile) as infile:
        csv_reader = DictReader(infile)
        places = {}
        for row in csv_reader:
            nation = row["country"]
            person = row["person"]

            location_category = None
            if row["location"]:
                location_category, location = palaces.get_location_category(row["location"], nation)
            if not location_category:
                location_category, location = palaces.get_location_category(row["title"], nation)
            if not location_category:
                location_category, location = palaces.get_location_category(row["description"], nation)

            if person not in places:
                places[person] = {
                    palaces.UNKNOWN: 0,
                    palaces.AT_HOME: 0,
                    palaces.DOMESTIC: 0,
                    palaces.ABROAD: 0
                }
            places[person][location_category] += 1
            outputrow = row
            outputrow["location_category"] = palaces.category_names[location_category]
            outputrow["location_name"] = location
            output.append(outputrow)
        print places

    with open('output.csv', 'w') as csvfile:
        fieldnames = ["id",
                      "description",
                      "title",
                      "country",
                      "date_end",
                      "date_start",
                      "person",
                      "link",
                      "location",
                      "location_category",
                      "location_name"]
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)


if __name__ == '__main__':
    main()
