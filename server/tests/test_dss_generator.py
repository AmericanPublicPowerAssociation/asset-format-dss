from asset_format_dss.routines.opendss import generate_dss_script
from conftest import EXAMPLE_BY_NAME

flat_assets = lambda l: [item for sublist in l for item in sublist]


class DataValidationError(Exception):
    pass


def test_dss_generation_circuit():
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets'].values()
    assets = flat_assets(assets)
    buses = [bus['id'] for bus in bus13_example['buses']]
    connections = bus13_example['connections']
    line_codes = bus13_example['line_codes']

    script = generate_dss_script(assets, connections, buses, line_codes)