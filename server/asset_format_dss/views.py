from asset_tracker.models.asset import Asset, Connection, Bus, LineType
from io import StringIO
from pyramid.response import Response
from pyramid.view import view_config

from .routines.opendss import generate_dss_script, normalize_assets_and_connections, line_types_to_json, \
    remove_temporal_line_connections


@view_config(
    route_name='assets.dss',
    request_method='GET')
def see_assets_dss(request):
    db = request.db
    vsourceId = request.GET.get('sourceId')
    print(vsourceId)
    element = db.query(Asset).filter(Asset.id == vsourceId)
    print(element.count())
    connections = db.query(Connection).all()
    assets = db.query(Asset).filter(Asset.is_deleted == False)

    line_types = line_types_to_json(db.query(LineType).all())

    # Asset filters and transformers
    temporal_assets, temporal_connections = remove_temporal_line_connections(assets, connections)
    normalized_assets, normalized_conn = normalize_assets_and_connections(temporal_assets, temporal_connections)
    buses = [connection['bus_id'] for connection in normalized_conn]
    if element.count():
        script = generate_dss_script(normalized_assets, normalized_conn, buses, line_types, root=element.one().id)
    else:
        script = generate_dss_script(normalized_assets, normalized_conn, buses, line_types)

    f = StringIO()

    for line in script:
        f.write(line)

    return Response(
        body=f.getvalue(),
        status=200,
        content_type='text/plain',
        content_disposition='attachment; filename="assets.dss"')
