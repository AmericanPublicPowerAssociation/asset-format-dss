def includeme(config):
    config.include('.constants')
    config.include('.routes')
    config.scan()
