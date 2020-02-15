from os.path import join

from asset_tracker.macros import load_json
from asset_tracker.routines.assets import absorb_asset_types

from . import CONSTANTS_FOLDER


def includeme(config):
    absorb_asset_types(ASSET_TYPES)


ASSET_TYPES = load_json(join(CONSTANTS_FOLDER, 'assetTypes.json'))
