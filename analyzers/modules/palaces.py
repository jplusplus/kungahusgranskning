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
palaces_strong = [
    u"audience",
    u"audiens",
    u"Audience",
    u"Audiens",
    u"Statsråd",
    u"Företräde för",
    u"er rigsforstander",
    u"er regent",
    u"er værter",
    u"Utrikesnämnd",
    u"Kronprinsessans födelsedag",
    u"Te Deum",
    u"konselj",
    u"Konselj",

    u"Det kongelige slott",
    u"Åpent Slott",
    u"åpent Slott",
    u"viser sig på balkongen",
    u"viser sig på balkonen",
    u"Christiansborg Slot",
    u"Marselisborg Slot",
    u"Fredensborg Slot",
    u"Christian VII's Palæ",
    u"Amalienborg",
    u"Gråsten Slot",
    u"Kongeskibet",
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
    u"Drottningholm",
    u"konselj",
    u"Gripsholm",
    u"Hagaparken",
    u"Bernadottebiblioteket",
]

palaces_weak = [
    u"företräde för",
    u"modtager",
    u"mottagning",
    u"Mottagning",
    u"afholder pressemøde",
    u"Statsbesök från ",
    u"Lunch för ",
    u"afholder gallataffel",
    u"fødselsdag",
    u"födelsedag",
]

place_name_patterns = [
    # pylint: disable=E501
    u"((([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ,i]+)+)?[A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d\d\.\d\d\)",  # Grünerløkka i Oslo (11.00)
    u"(([A-ZÅÄÖØÆ][a-zåäöøæüñ]+[ ])+, ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+))$",  # Silicon Valley, USA
    u" i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.",  # i Roma.
    u"[bB]es[öø][gk] i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # Besök i Peru och Bolivia
    u"[bB]es[öø][gk] på ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # Besök på Gotland
    u"[bB]es[öø][gk] til ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # besøk til Italia besøg
    u"[rR]ejser? til ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # rejse til Italia
    u"[An]nkommer till? ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # ankomer til Italia
    u"[bB]es[öø][gk]er ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)",  # besøker Italia
    u", ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # , Stockholm
    u" i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.?$",  # i Roma.
    u" till? ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)\.?$",  # til Roma.
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d{1,2}\.",  # Oslo (11.00)
    u"\(([A-ZÅÄÖØÆ][a-zåäöøæüñ]+), \d\d\.\d\d\)",  # (Holmenkollen, 11.30).
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+), \d{1,2}\.",  # , Tromsø, 29. - 31. januar
    u"([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) den \d{1,2}\.",  # Tromsø den 29. - 31. januar
    u"på ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \d{1,2}\.",  # på Tromsø 29. - 31. januar
    u"i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \d{1,2}\.",  # i Tromsø 29. - 31. januar
    u"i ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+) kl\. \d{1,2}\.",  # i Tromsø 29. - 31. januar
    u"^([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # Stockholm
    u"och ([A-ZÅÄÖØÆ][a-zåäöøæüñ]+)$",  # Umeå och Stockholm
    u"^([A-ZÅÄÖØÆ][a-zåäöøæüñ]+ [A-ZÅÄÖØÆ]?[a-zåäöøæüñ]+)$",  # Uppsala domkyrka
]

"""Place names and other words that indicate that the royal family member
   is at a domestic function. These will be used as a last resort.
"""
domestic = [
    u"invigning",
    u"Invigning",
    u"inviger",
    u"indvielse",
    u"indvier",
    u"innsettelse",
    u"åbning",
    u"åpning",
    u"Nobel",
    u"Närvaro vid ",
    u"Besök hos ",

]


class NotFoundError(StandardError):
    pass


class GeoCodingError(StandardError):
    pass


def contains_palace_name(text, namelist=palaces_strong):
    for palace in namelist:
        if palace in text:
            return True
    raise NotFoundError


def looks_domestic(text):
    for word in domestic:
        if word in text:
            return True
    raise NotFoundError


def get_place_names(text):
    placenames = []
    for place_name_pattern in place_name_patterns:
        p = re.compile(place_name_pattern)
        matches = p.search(text)
        if matches:
            placenames.append(matches.groups()[0])
    if len(placenames):
        return placenames
    else:
        raise NotFoundError


def geoposition(text):
    """ Use Google Maps API to geocode string """
    store = FilesystemStore('./cache')
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false&language=sv" % text
    cache_key = md5.new(text.encode('utf-8')).hexdigest()
    try:
        result = store.get(cache_key)
        if loads(result):
            return loads(result)
        else:
            raise GeoCodingError

    except KeyError:
        print "no cache for %s" % text.encode('utf-8')
        sleep(2)  # Sleep to avoid being blocked by Google Maps API
        result = requests.get(url).json()
        if len(result["results"]):
            store.put(cache_key, dumps(result["results"][0]))
            return result["results"][0]
        else:
#            print "empty reply when geocoding %s" % text
            store.put(cache_key, dumps(None))
            raise GeoCodingError


def get_names_and_geocode(text):
    """Try and geocode things that look like place names
    """
    placenames = get_place_names(text)
    for placename in placenames:
        try:
            return geoposition(placename)
        except GeoCodingError:
            pass
    raise NotFoundError


def get_location_category(text, nation):
    """Use all available methods, return first match"""

    try:
        if contains_palace_name(text, palaces_strong):
            return (AT_HOME, None)
    except NotFoundError:
        pass

    try:
        placepos = get_names_and_geocode(text)
        for component in placepos["address_components"]:
            if "country" in component["types"]:
                if nation == component["long_name"]:
                    return (DOMESTIC, component["long_name"])
                else:
                    return (ABROAD, component["long_name"])
        return (UNKNOWN, None)
    except NotFoundError:
        pass
    except TypeError:
        pass

    try:
        if looks_domestic(text):
            return (DOMESTIC, None)
    except NotFoundError:
        pass

    try:
        if contains_palace_name(text, palaces_weak):
            return (AT_HOME, None)
    except NotFoundError:
        pass

    return (UNKNOWN, None)
