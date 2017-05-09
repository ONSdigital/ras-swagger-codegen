#!/usr/bin/python3

from sys import argv
from json import loads, dumps

API_PATH = '/party-api/1.0.1/'
API_HOST = 'localhost'

with open(argv[1]) as io:
	buffer = loads(io.read())

buffer['basePath'] = API_PATH
buffer['host'] = API_HOST

with open(argv[1], 'w') as io:
	io.write(dumps(buffer))
