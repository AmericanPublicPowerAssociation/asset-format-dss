import json
from os.path import join

from asset_tracker.routines.assets import absorb_asset_types

from . import CONSTANTS_FOLDER


def includeme(config):
    absorb_asset_types(ASSET_TYPES)


ASSET_TYPES_PATH = join(CONSTANTS_FOLDER, 'assetTypes.json')
ASSET_TYPES = json.load(open(ASSET_TYPES_PATH, 'rt'))
