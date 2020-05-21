from os.path import dirname, join


def includeme(config):
    config.include('.asset')


PACKAGE_FOLDER = dirname(dirname(__file__))
DATASETS_FOLDER = join(PACKAGE_FOLDER, 'datasets')
