#!/usr/bin/env python3

from connexion import App
from .encoder import JSONEncoder
from os import getenv, getcwd
from pathlib import Path

if __name__ == '__main__':
    cf_app_env = getenv('VCAP_APPLICATION')
    if cf_app_env is not None:
        import yaml
        import json
        cwd = getcwd()
        config = './swagger_server/swagger/swagger.yaml'
        if Path(config).is_file():
            with open(config) as io:
                code = yaml.load(io)
            code['host'] = json.loads(cf_app_env)['application_uris'][0]
            with open(config, 'w') as io:
                io.write(yaml.dump(code))

    app = App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'ONS Microservice'})
    app.run(host='0.0.0.0', port=getenv('PORT', 8080))

    #from twisted.internet import reactor
    #from flask_twisted import Twisted
    #reactor.callLater(1, print, '<<Twisted is running>>')
    #Twisted(app).run(port=getenv('PORT',8080))

