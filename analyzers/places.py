# encoding: utf-8
"""Categorize events according to where they took place
"""

from modules import Interface


def main():
    """ Entry point when run from command line
    """
    # pylint: disable=C0103

    cmd_args = []
    ui = Interface("BlockePlaces",
                   "Find out where events took place",
                   commandline_args=cmd_args)
    ui.exit()

if __name__ == '__main__':
    main()
