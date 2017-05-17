#!/bin/bash
if ! [ -a .build ] ; then
	echo "Creating Virtual Environment"
	virtualenv .build -p python3
fi
source .build/bin/activate
pip3 -q install -r requirements.txt
pytest --cov=swagger_server/controllers_local --cov-report term-missing
