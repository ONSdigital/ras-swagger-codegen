#!/usr/bin/python3

from urllib.request import urlopen
from pathlib import Path
from filecmp import cmp
from json import loads, dumps
from os import rename
from shutil import copyfile
from sys import argv
from subprocess import run, PIPE

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
        print('@ Regenerating "{}"'.format(api))
        page = urlopen('https://api.swaggerhub.com/apis/{}/{}/{}'.format(url, api, ver))
        json = page.read()
        print('@ Downloaded new API spec, "{}" bytes'.format(len(json)))

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
        run(['rm', '../ras-rapos/{}/requirements.txt'.format(rep)])
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
        copyfile('templates/__main__.py', rep)
        copyfile('templates/Procfile', rep)
        copyfile('templates/run.sh', rep)
