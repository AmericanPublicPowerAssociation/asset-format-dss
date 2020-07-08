from os.path import dirname, join
from invisibleroads_macros_configuration import load_json


def load_example_json(example_name):
    return load_json(join(EXAMPLES_FOLDER, example_name))



TESTS_FOLDER = dirname(__file__)
EXAMPLES_FOLDER = join(TESTS_FOLDER, 'examples')
EXAMPLE_BY_NAME = {
    'bus13': load_example_json('bus13.json'),
}

pytest_plugins = [
    'invisibleroads_posts.tests',
    'invisibleroads_records.tests',
    'asset_tracker.tests',
]
