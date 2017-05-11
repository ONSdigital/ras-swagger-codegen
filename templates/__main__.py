#!/usr/bin/env python3

import connexion
from encoder import JSONEncoder
from twisted.internet import reactor
from flask_twisted import Twisted
from os import getenv


if __name__ == '__main__':
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Initial API for the Party microservice.'})
    app.run(port=getenv('PORT',8080), debug=True)
    #reactor.callLater(1, print, '<<Twisted is running>>')
    #Twisted(app).run(port=getenv('PORT',8080))
