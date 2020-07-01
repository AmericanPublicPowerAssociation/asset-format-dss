from asset_tracker.models.asset import Asset, Connection, Bus, LineType
from io import StringIO
from pyramid.response import Response
from pyramid.view import view_config

from .routines.opendss import generate_dss_script, normalize_assets_and_connections, line_types_to_json


@view_config(
    route_name='assets.dss',
    request_method='GET')
def see_assets_dss(request):
    db = request.db
    vsourceId = request.GET.get('sourceId')

    element = db.query(Asset).filter(Asset.id == vsourceId)

    connections = db.query(Connection).all()
    assets = db.query(Asset).filter(Asset.is_deleted == False)
    buses = [bus.id for bus in db.query(Bus).all()]
    line_types = line_types_to_json(db.query(LineType).all())
    normalized_assets, normalized_conn = normalize_assets_and_connections(assets, connections)

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
