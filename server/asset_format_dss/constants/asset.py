from invisibleroads_macros_configuration import load_json
from os.path import join

from asset_tracker.routines.asset import absorb_asset_type_by_code

from . import DATASETS_FOLDER


def includeme(config):
    absorb_asset_type_by_code(ASSET_TYPE_BY_CODE)


ASSET_TYPE_BY_CODE = load_json(join(DATASETS_FOLDER, 'assetTypeByCode.json'))
