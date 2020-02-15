from os.path import dirname


def includeme(config):
    config.include('.assets')


CONSTANTS_FOLDER = dirname(__file__)
PACKAGE_FOLDER = dirname(CONSTANTS_FOLDER)
