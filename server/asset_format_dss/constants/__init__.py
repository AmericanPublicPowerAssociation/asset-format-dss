from os.path import dirname, join


def includeme(config):
    config.include('.assets')


PACKAGE_FOLDER = dirname(__file__)
DATASETS_FOLDER = join(PACKAGE_FOLDER, 'datasets')
