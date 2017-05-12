#!/usr/bin/python3

from urllib.request import urlopen
from pathlib import Path
from filecmp import cmp
from json import loads, dumps
from os import rename, makedirs
from shutil import copy
from sys import argv
from subprocess import run, PIPE
from yaml_tool import YAML_API

force = '-f' in argv

with open('packages.txt') as packages:
    while True:
        line = packages.readline()
        if not line:
            break
        parts = line.split(" ")
        if parts[0] == '#':
            continue
        if len(parts) != 5:
            print('%% ignoring :: ', line)
            continue

        api, ver, rep, url, host = parts
        print("Repo+", rep)
        print('@ Regenerating "{}"'.format(api))
        page = urlopen('https://api.swaggerhub.com/apis/{}/{}/{}'.format(url, api, ver))
        json = page.read()
        print('@ Downloaded new API spec, "{}" bytes'.format(len(json)))

        if not Path('apis').is_dir():
            makedirs('apis')

        oldfile = 'apis/{}-{}-{}.json'.format(url, api, ver)
        newfile = 'apis/{}-{}-{}.json.new'.format(url, api, ver)
        if not Path(oldfile).is_file():
            name = oldfile
        else:
            name = newfile

        with open(name, 'w') as io:
            io.write(json.decode())
        if name == oldfile:
            generate = True
        else:
            generate = not cmp(oldfile, newfile)

        if not generate and not force:
            print('@ No changes ...')
            continue

        if name == newfile:
            rename(newfile, oldfile)
        print('@ Updating metadata for "{}"'.format(api))
        with open(oldfile) as io:
            buffer = loads(io.read())

        buffer['basePath'] = '/{}/{}'.format(api, ver)
        buffer['host'] = host
        with open('apis/config.json', 'w') as io:
            io.write(dumps(buffer))

        print('@ Running code generator for "{}"'.format(api))
        run([
            'pwd'
        ])
        status = run([
            "java", "-jar", "/usr/local/bin/swagger-codegen-cli.jar", "generate",
            "-i", "apis/config.json",
            "-l", "python-flask",
            "-o../ras-repos/{}".format(rep)
        ], stdout=PIPE)
        if status.returncode:
            print('%% code generation FAILED!')
            exit(status.returncode)

        target = '../ras-repos/{}/'.format(rep)
        copy('templates/__main__.py', target + 'swagger_server/__main__.py')
        copy('templates/Procfile', target + 'Procfile')
        copy('templates/run.sh', target + 'run.sh')
        copy('templates/runtime.txt', target + 'runtime.txt')

        def ensure_line(filename, test):
            with open(filename) as inp:
                text = inp.read()
            if test not in text:
                with open(filename, 'a') as out:
                    out.write(test)

        with open('templates/requirements.txt') as io:
            while True:
                line = io.readline()
                if not line:
                    break
                ensure_line('../ras-repos/{}/requirements.txt'.format(rep), line)

        print('* Running YAML router for "{}"'.format(rep))
        api = YAML_API()
        api.open(rep)
        api.load_tags()
        api.load_controllers()
        api.route()
