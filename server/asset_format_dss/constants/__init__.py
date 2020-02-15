from os.path import dirname

from asset_tracker import constants


def includeme(config):
    pass


CONSTANTS_FOLDER = dirname(__file__)
PACKAGE_FOLDER = dirname(CONSTANTS_FOLDER)
