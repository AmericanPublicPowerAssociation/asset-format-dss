from asset_tracker.models.asset import Asset, Connection, LineType
from io import StringIO
from pyramid.response import Response
from pyramid.view import view_config

from .routines.opendss import (
    generate_dss_script,
    line_types_to_json,
    normalize_assets_and_connections,
    remove_temporal_line_connections)


@view_config(
    route_name='assets.dss',
    request_method='GET')
def see_assets_dss(request):
    db = request.db
    viewable_assets_query = Asset.get_viewable_query(
        request, with_connections=False)
    vsourceId = request.GET.get('sourceId')

    element = viewable_assets_query.filter(Asset.id == vsourceId).first()

    connections = db.query(Connection).all()
    assets = viewable_assets_query.all()
    line_types = line_types_to_json(db.query(LineType).all())

    # Asset filters and transformers
    temporal_assets, temporal_connections = remove_temporal_line_connections(
        assets, connections)
    normalized_assets, normalized_conn = normalize_assets_and_connections(
        temporal_assets, temporal_connections)
    buses = [connection['bus_id'] for connection in normalized_conn]
    if element:
        lines = generate_dss_script(
            normalized_assets, normalized_conn, buses, line_types,
            root=element.id)
    else:
        lines = generate_dss_script(
            normalized_assets, normalized_conn, buses, line_types)
    return Response(
        body=StringIO(''.join(lines)).getvalue(),
        status=200,
        content_type='text/plain',
        content_disposition='attachment; filename="assets.dss"')
