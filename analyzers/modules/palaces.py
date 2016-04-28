# encoding: utf-8
""" Helper functions and classes for determining the location of royal events
"""
import re
import requests
from time import sleep
from simplekv.fs import FilesystemStore
from json import dumps, loads
import md5


"""Place categories"""
UNKNOWN = 0
AT_HOME = 1
NEAR_HOME = 2
DOMESTIC = 3
ABROAD = 4

category_names = {
    UNKNOWN: "",
    AT_HOME: "slottet",
    NEAR_HOME: "huvudstaden",
    DOMESTIC: "inrikes",
    ABROAD: "utrikes"
}


"""Place names and other that indicate that the royal family member
   is at home
"""
palaces = [
    u"audience",
    u"audiens",
    u"Audience",
    u"Audiens",
    u"Det kongelige slott",
    u"viser sig på balkongen",
    u"Christiansborg Slot",
    u"Marselisborg Slot",
    u"Fredensborg Slot",
    u"Christian VII's Palæ",
    u"Amalienborg",
    u"Gråsten Slot",
    u"Château de Cayx",
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
    u"Te Deum",
]

place_name_patterns = [
    # pylint: disable=E501
    u"((([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ,i]+)+)?[A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d\d\.\d\d\)",  # Grünerløkka i Oslo (11.00)
    u"(([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ])+, ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+))$",  # Silicon Valley, USA
    u" i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.",  # i Roma.
    u"[bB]es[öø][gk] i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # Besök i Peru och Bolivia
    u"[bB]es[öø][gk] til ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # besøk til Italia besøg
    u"[rR]ejser? til ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # rejse til Italia
    u", ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # , Stockholm
    u" i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.?$",  # i Roma.
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d\d\.\d\d\)",  # Oslo (11.00)
    u"\(([A-ZÅÄÖØÆ][a-zåäöøæüñ]+), \d\d\.\d\d\)",  # (Holmenkollen, 11.30).
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+), \d{1,2}\.",  # , Tromsø, 29. - 31. januar
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) den \d{1,2}\.",  # Tromsø den 29. - 31. januar
    u"[bB]es[öø]ker ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # besøker Italia
    u"^([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # Stockholm
    u"och ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # Umeå och Stockholm
]


class NotFoundError(StandardError):
    pass


class GeoCodingError(StandardError):
    pass


def contains_palace_name(text):
    for palace in palaces:
        if palace in text:
            return True
    raise NotFoundError


def get_place_name(text, reverse=False):
    matches = []
    if reverse is True:
        patterns = place_name_patterns[::-1]
    else:
        patterns = place_name_patterns
    for place_name_pattern in patterns:
        p = re.compile(place_name_pattern)
        matches = p.search(text)
        if matches:
            return matches.groups()[0]
    raise NotFoundError


def geoposition(text):
    """ Use Google Maps API to geocode string """
    store = FilesystemStore('./cache')
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&language=sv" % text
    cache_key = md5.new(text.encode('utf-8')).hexdigest()
    try:
        result = store.get(cache_key)
        return loads(result)
    except KeyError:
        sleep(2)  # Sleep to avoid being blocked by Google Maps API
        result = requests.get(url).json()
        if len(result["results"]):
            store.put(cache_key, dumps(result["results"][0]))
            return result["results"][0]
        else:
            raise GeoCodingError


def get_names_and_geocode(text):
    """Try and geocode things that look like place names
    """
    placename = None
    try:
        placename = get_place_name(text)
        print u"trying to geocode “%s” from %s" % (placename, text)
        return geoposition(placename)
    except GeoCodingError:
        pass
#        print u"Failed to geocode “%s” from “%s”, trying a different algorithm" % (placename, text)

    try:
        placename2 = get_place_name(text, reverse=True)
        if placename != placename2:
            print u"Failed. Trying to geocode “%s” from %s" % (placename2, text)
            return geoposition(placename)
    except GeoCodingError:
        pass
#        print u"Failed to geocode “%s” from “%s”, giving up" % (placename, text)

    raise NotFoundError


def get_location_category(text, nation):
    """Use all available method, return first match"""
    try:
        if contains_palace_name(text):
            return AT_HOME
    except NotFoundError:
        pass

    try:
        placepos = get_names_and_geocode(text)
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
