#!/usr/bin/python3

import configparser
from filecmp import cmp
from json import loads, dumps
from os import rename, makedirs
from pathlib import Path
from subprocess import run, PIPE
from sys import argv
from urllib.request import urlopen

from yaml_tool import YAML_API

force = '-f' in argv


config = configparser.ConfigParser()
config.read('config.ini')
repo_path = config.get('CodeGen', 'repo_path', fallback="../ras-repos")
generator_command = config.get('CodeGen', 'generator_command',
                               fallback="java -jar /usr/local/bin/swagger-codegen-cli.jar")

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
        run(['rm', '-rf', '{}/{}/swagger_server/test'.format(repo_path, rep)])
        run(['rm', '-rf',  '{}/{}/swagger_server/controllers'.format(repo_path, rep)])

        status = run(generator_command.split() + [
            "generate",
            "-i", "apis/config.json",
            "-l", "python-flask",
            "-o{}/{}".format(repo_path, rep)
        ], stdout=PIPE)
        if status.returncode:
            print('%% code generation FAILED!')
            exit(status.returncode)

        run(['rm', '{}/{}/git_push.sh'.format(repo_path, rep)])
        target = '{}/{}/'.format(repo_path, rep)
        makedirs(target+'scripts', exist_ok=True)
        makedirs(target+'swagger_server/test_local', exist_ok=True)
        makedirs(target+'swagger_server/controllers_local', exist_ok=True)
        files = [
            ['__main__.py', 'swagger_server/__main__.py'],
            ['Procfile'],
            ['runtime.txt'],
            ['.travis.yml'],
            ['requirements_for_test.txt'],
            ['requirements.txt'],
            ['config.ini'],
            ['configuration.py', 'swagger_server/configuration.py'],
            ['encryption.py', 'swagger_server/controllers_local/encryption.py'],
            ['test/__init__.py', 'swagger_server/test/__init__.py'],
            ['test/__init__.py', 'swagger_server/test_local/__init__.py'],
            ['scripts/run.sh'],
            ['scripts/git_push.sh'],
            ['scripts/test.sh'],
            ['scripts/run_tests.sh'],
            ['scripts/run_unit_tests.sh'],
            ['scripts/run_linting.sh']
        ]
        for file in files:
            if len(file) > 1:
                run(['cp', 'templates/'+file[0], target + file[1]])
            else:
                run(['cp', 'templates/'+file[0], target + file[0]])

        with open('templates/scripts/cckeys.json') as cc:
            keys = loads(cc.read())
            if rep in keys:
                fname = '{}/{}/.travis.yml'.format(repo_path, rep)
                with open(fname, 'a') as kk:
                    kk.write('env:\n')
                    kk.write('  - secure: ')
                    kk.write(keys[rep])
                    kk.write('\n')

        print('* Running YAML router for "{}"'.format(rep))
        api = YAML_API(config)
        api.open(rep)
        api.load_tags()
        api.load_controllers()
        api.route()

        #def ensure_line(filename, test):
        #    with open(filename) as inp:
        #        text = inp.read()
        #    if test not in text:
        #        with open(filename, 'a') as out:
        #            out.write(test)

        #with open('templates/requirements.txt') as io:
        #    while True:
        #        line = io.readline()
        #        if not line:
        #            break
        #        ensure_line('{}/{}/requirements.txt'.format(repo_path, rep), line)
