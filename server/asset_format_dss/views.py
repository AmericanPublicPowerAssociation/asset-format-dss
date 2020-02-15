from pyramid.view import view_config


@view_config(
    route_name='assets.dss',
    request_method='GET')
def see_assets_dss(request):
    pass
