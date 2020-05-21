from os.path import join

from invisibleroads_macros_configuration import load_json
# from asset_tracker.routines.asset import absorb_asset_type_by_code

from . import CONSTANTS_FOLDER


def includeme(config):
    # absorb_asset_type_by_code(ASSET_TYPES)
    pass



ASSET_TYPES = load_json(join(CONSTANTS_FOLDER, 'assetTypes.json'))
