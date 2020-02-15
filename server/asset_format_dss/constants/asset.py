import json
from os.path import join

from . import CONSTANTS_FOLDER


ASSET_TYPES_PATH = join(CONSTANTS_FOLDER, 'assetTypes.json')
ASSET_TYPES = json.load(open(ASSET_TYPES_PATH, 'rt'))
