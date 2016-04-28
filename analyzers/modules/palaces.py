# encoding: utf-8
""" Helper functions and classes for determining the location of royal events
"""
import re
import requests
from time import sleep

"""Place categories"""
UNKNOWN = 0
AT_HOME = 1
NEAR_HOME = 2
DOMESTIC = 3
ABROAD = 4

category_names = {
    UNKNOWN: "",
    AT_HOME: "slottet",
    DOMESTIC: "inrikes",
    ABROAD: "utrikes"
}


"""Place names and other that indicate that the royal family member
   is at home
"""
palaces = [
    u"audience",
    u"Det kongelige slott",
    u"viser sig på balkongen",
    u"Christiansborg Slot",
    u"Marselisborg Slot",
    u"Fredensborg Slot",
    u"Christian VII's Palæ",
    u"Amalienborg",
    u"Gråsten Slot",
    u"på Slottsplassen",
    u"Oscarshall",
    u"Kungliga slottet",
    u"Slottskapellet",
    u"slottsbalkongen",
    u"Hovstallet",
    u"Lejonbacken",
    u"Yttre borggården",
    u"Ulriksdal",
    u"konselj",
    u"Gripsholm",
    u"Hagaparken",
    u"Bernadottebiblioteket",
]

place_name_patterns = [
    # pylint: disable=E501
    "((([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ,i]+)+)?[A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d\d\.\d\d\)",  # Grünerløkka i Oslo (11.00)
    " i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.$",  # i Roma.
    " i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.",  # i Roma.
    " i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # i Peru
    "(([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ])+, ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+))$",  # Silicon Valley, USA
    ", ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # , Stockholm
    "[bB]es[öø]k i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # Besök i Peru och Bolivia
]


class NotFoundError(StandardError):
    pass


class GeoCodingError(StandardError):
    pass


def contains_palace_name(text):
    for palace in palaces:
        if palace in text:
            return (True)
    raise NotFoundError


def get_place_name(text):
    matches = []
    for place_name_pattern in place_name_patterns:
        p = re.compile(place_name_pattern)
        matches = p.search(text)
        if matches:
            return matches.groups()[0]
    raise NotFoundError


def geoposition(text):
    """ Use Google Maps API to geocode string """
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&language=sv" % text
    result = requests.get(url).json()
    if len(result["results"]):
        return result["results"][0]
    else:
        raise GeoCodingError


def get_location_category(text, nation):
    """Use all available method, return first match"""
    try:
        if contains_palace_name(text):
            return AT_HOME
    except NotFoundError:
        pass

    try:
        placename = get_place_name(text)
        print "Placename: %s" % placename
        try:
            sleep(2)
            placepos = geoposition(placename)
        except GeoCodingError:
            print "Failed to geocode %s" % placename
            return UNKNOWN
        for component in placepos["address_components"]:
            if "country" in component["types"]:
                if nation == component["long_name"]:
                    return DOMESTIC
                else:
                    return ABROAD
        return UNKNOWN
    except NotFoundError:
        pass

    return UNKNOWN
