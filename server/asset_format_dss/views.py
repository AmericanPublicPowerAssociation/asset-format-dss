from asset_tracker.models import Asset
from io import StringIO
from pyramid.response import Response
from pyramid.view import view_config

from .routines.opendss import generate_dss_script


@view_config(
    route_name='assets.dss',
    request_method='GET')
def see_assets_dss(request):
    db = request.db
    vsourceId = request.GET.get('sourceId')

    element = db.query(Asset).filter(Asset.id == vsourceId)
    if element.count():
        script = generate_dss_script(request.db, root=element.one().id)
    else:
        script = generate_dss_script(request.db)

    f = StringIO()

    for line in script:
        f.write(line)

    return Response(
        body=f.getvalue(),
        status=200,
        content_type='text/plain',
        content_disposition='attachment; filename="assets.dss"')
