from functools import reduce

from asset_format_dss.routines.opendss import generate_dss_script
from asset_format_dss.views import see_assets_dss

from asset_tracker.routines.asset import update_assets, update_asset_connections
from asset_tracker.macros.database import RecordIdMirror
from asset_tracker.models import Asset
from conftest import EXAMPLE_BY_NAME


def flat_assets(nested_assets):
    return [item for sublist in nested_assets for item in sublist]


def get_connections_as_indexed_dict(connections, asset_id):
    connections = list(filter(lambda connection: connection['asset_id'] == asset_id, connections))
    num_connections = len(connections)
    connections_by_index = {
        str(index):  {
            'busId': connection['bus_id'],
            'attributes': connection['attributes']
        } for index, connection in zip(range(num_connections), connections)}

    return connections_by_index


def populate_bus13(database):
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets'].values()
    connections = bus13_example['connections']
    assets = {
        asset['id']: {
            **asset,
            'name': asset['id'],
            'typeCode': asset['type_code'],
            'connections': get_connections_as_indexed_dict(connections, asset['id'])
        } for asset in flat_assets(assets)}

    asset_id_mirror = RecordIdMirror()

    update_assets(database, assets, asset_id_mirror)
    update_asset_connections(database, assets, asset_id_mirror)


def count_dss_instructions(target_instruction, instructions):
    count_instructions = lambda counter, instruction: counter + 1 if target_instruction in instruction else counter
    return reduce(count_instructions, instructions, 0)


def test_bus13_assets(database):
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets'].values()
    assets = {
        asset['id']: {
            **asset,
            'name': asset['id'],
            'typeCode': asset['type_code'],
        } for asset in flat_assets(assets)}

    asset_id_mirror = RecordIdMirror()

    update_assets(database, assets, asset_id_mirror)


def test_bus13_connections(database):
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets'].values()
    connections = bus13_example['connections']
    assets = {
        asset['id']: {
            **asset,
            'name': asset['id'],
            'typeCode': asset['type_code'],
            'connections': get_connections_as_indexed_dict(connections, asset['id'])
        } for asset in flat_assets(assets)}

    asset_id_mirror = RecordIdMirror()

    update_assets(database, assets, asset_id_mirror)
    update_asset_connections(database, assets, asset_id_mirror)


def test_generate_bus13_dss_view(database, application_request):
    populate_bus13(database)
    asset = database.query(Asset).filter(Asset.name == 'voltageSource').one()
    application_request.GET['sourceId'] = asset.id

    response = see_assets_dss(application_request)

    assert response.status_code == 200
    assert response.has_body
    assert response.content_type == 'text/plain'

    instructions = response.text.split('\n')

    assert count_dss_instructions('Edit Vsource.Source', instructions) == 1
    assert count_dss_instructions('New Transformer.', instructions) == 5
    assert count_dss_instructions('New Load.', instructions) == 14
    assert count_dss_instructions('New Line.', instructions) == 11
    assert count_dss_instructions('New regcontrol.', instructions) == 3
    assert count_dss_instructions('New Generator.', instructions) == 0


def test_generate_dss_view_without_source_voltage(database, application_request):
    populate_bus13(database)
    response = see_assets_dss(application_request)

    assert response.status_code == 200
    assert response.has_body
    assert response.content_type == 'text/plain'

    instructions = response.text.split('\n')

    assert count_dss_instructions('// WARNING: No voltage source provided or the source id is invalid', instructions) == 1
    assert count_dss_instructions('Edit Vsource.Source', instructions) == 0
    assert count_dss_instructions('New Transformer.', instructions) == 5
    assert count_dss_instructions('New Load.', instructions) == 14
    assert count_dss_instructions('New Line.', instructions) == 11
    assert count_dss_instructions('New regcontrol.', instructions) == 3
    assert count_dss_instructions('New Generator.', instructions) == 1


def test_dss_generation_circuit():
    bus13_example = EXAMPLE_BY_NAME['bus13']
    assets = bus13_example['assets'].values()
    assets = flat_assets(assets)
    buses = [bus['id'] for bus in bus13_example['buses']]
    connections = bus13_example['connections']
    line_codes = bus13_example['line_codes']

    script = generate_dss_script(assets, connections, buses, line_codes)

# Check line types