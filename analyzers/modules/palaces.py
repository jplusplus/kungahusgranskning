# encoding: utf-8
""" Helper functions and classes for determining the location of royal events
"""
import re

"""Place categories"""
UNKNOWN = 0
AT_HOME = 1
NEAR_HOME = 2
DOMESTIC = 3
ABROAD = 4


"""Place names and other that indicate that the royal family member
   is at home
"""
palaces = [
    u"audience",
    u"Det kongelige slott",
    u"viser sig på balkonen",
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
    u"Hovstallet",
    u"Lejonbacken",
    u"Yttre borggården",
    u"Ulriksdal",
    u"konselj",
    u"Gripsholm",
]

place_name_patterns = [
    # pylint: disable=E501
    "(([A-ZÅÄÖØÆ][a-zåäöøæüñ][ ,])?(i )?[A-ZÅÄÖØÆ][a-zåäöøæüñ]+) \(\d\d\.\d\d\)",  # H.M. Dronningen besøker Sofienberghjemmet på Grünerløkka i Oslo (11.00).
]


class NotFoundError(StandardError):
    pass


def contains_palace_name(text):
    for palace in palaces:
        if palace in text:
            return True
    raise NotFoundError


def get_place_name(text):
    matches = []
    for place_name_pattern in place_name_patterns:
        p = re.compile(place_name_pattern)
        matches = p.search(text)
        if matches:
            print matches.groups()  
            return None
    raise NotFoundError
