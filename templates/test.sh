#!/bin/bash
source .build/bin/activate
pytest --cov=swagger_server/controllers_local --cov-report term-missing
