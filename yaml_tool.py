#!/usr/bin/python3

from sys import argv
from os import makedirs, rename
import yaml
from pathlib import Path


LOCAL = '{}/{}/swagger_server/controllers_local/{}_controller.py'
GENERIC = '{}/{}/swagger_server/controllers/{}_controller.py'
YAML_FILE = '{}/{}/swagger_server/swagger/swagger.yaml'


def usage(msg):
    print('%% ', msg)
    print('Usage: {} <repo> [cmd [options]]'.format(argv[0]))
    print(' status - show brief status of repo')
    print(' list   - list which endpoints have been implemented')
    print(' route  - write changes into the swagger.yaml routing file')
    print(' implement [endpoint] - add a new implementation based on the implemented function name')
    exit(1)


class YAML_API(object):

    def __init__(self, user_config):
        self.tags = {}
        self.controllers = {}
        self.conf = None
        self.repo = None
        self.repo_path = user_config.get('CodeGen', 'repo_path', fallback='../ras-repos')

    def open(self, name):

        for folder in ['controllers_local', 'test_local']:
            pathname = '{}/{}/swagger_server/{}'.format(self.repo_path, name, folder)
            makedirs(pathname, exist_ok=True)

        pathname = YAML_FILE.format(self.repo_path, name)
        if not Path(pathname).is_file:
            print('%% unable to locate "{}"'.format(pathname))
            exit(1)
        with open(pathname) as io:
            self.conf = yaml.load(io)
        self.repo = name

    def save(self):
        file_name = YAML_FILE.format(self.repo_path, self.repo)
        rename(file_name, file_name+'.orig')
        with open(file_name, 'w') as io:
            io.write(yaml.dump(self.conf))

    def load_tags(self):
        for pth in self.conf['paths']:
            for method in self.conf['paths'][pth]:
                for tag in self.conf['paths'][pth][method]['tags']:
                    if tag not in self.tags:
                        self.tags[tag] = {}
                    if pth not in self.tags[tag]:
                        self.tags[tag][pth] = []
                    self.tags[tag][pth].append((self.conf['paths'][pth][method]['operationId'], pth, method, tag))

    def load_controllers(self):
        for tag in self.tags:
            self.controllers[tag] = []
            for pth in self.tags[tag]:
                for endpoint in self.tags[tag][pth]:
                    self.controllers[tag].append(endpoint)

    def check_codegen(self):
        succ = 0
        fail = []
        for controller in self.controllers:
            pathname = GENERIC.format(self.repo_path, self.repo, controller)
            with open(pathname) as io:
                text = io.read()
                for fn, pth, _, _ in self.controllers[controller]:
                    if ('\ndef ' + fn + '(') in text:
                        succ += 1
                    else:
                        fail.append(fn)
        print('Controller Check, "{}" items OK'.format(succ))
        if len(fail):
            for item in fail:
                print('Missing> ', item)
                exit(1)

    def status(self):
        implemented = []
        count = 0
        for controller in self.controllers:
            pathname = LOCAL.format(self.repo_path, self.repo, controller)
            if Path(pathname).is_file():
                with open(pathname) as io:
                    text = io.read()
            else:
                text = ''
            for fn, pth, _, _ in self.controllers[controller]:
                count += 1
                if ('\ndef '+fn+'(') in text:
                    implemented.append(fn)

        if not count:
            print('Total of "{}" endpoints, no local code'.format(count))
        else:
            percent = int(100*(len(implemented)/count))
            print('Total of "{}" endpoints, "{}" implemented "{}"%'.format(count, len(implemented), percent))

    def implement(self, target):
        for controller in self.controllers:
            pathname = GENERIC.format(self.repo_path, self.repo, controller)
            if Path(pathname).is_file():
                with open(pathname) as io:
                    text = io.read()
                    for fn, pth, _, _ in self.controllers[controller]:
                        if target == fn:
                            try:
                                pathname = LOCAL.format(self.repo_path, self.repo, controller)
                                with open(pathname) as dst:
                                    code = dst.read()
                                if ('\ndef ' + fn + '(') in code:
                                    print('%% already implemented: "{}"'.format(fn))
                                    exit(1)
                            except FileNotFoundError:
                                pass
                            beg = text.index('def {}('.format(fn))
                            try:
                                end = text.index('\ndef ', beg)
                            except ValueError:
                                end = len(text)
                            snippet = text[beg:end-1]
                            pathname = LOCAL.format(self.repo_path, self.repo, controller)
                            with open(pathname, 'a') as dst:
                                dst.write('\n#\n# {}\n#\n'.format(pth))
                                dst.write(snippet)
                            return
        print('%% failed to find endpoint "{}"'.format(target))

    def list(self):
        implemented = []
        unimplemented = []
        count = 0
        for controller in self.controllers:
            pathname = LOCAL.format(self.repo_path, self.repo, controller)
            if Path(pathname).is_file():
                with open(pathname) as io:
                    text = io.read()
            else:
                text = ''
            for fn, pth, _, _ in self.controllers[controller]:
                count += 1
                if ('\ndef '+fn+'(') in text:
                    implemented.append((fn, pth))
                else:
                    unimplemented.append((fn, pth))

        for fn, pth in implemented:
            print('[X] {} :: {}'.format(fn, pth))
        for fn, pth in unimplemented:
            print('[ ] {} :: {}'.format(fn, pth))

    def update_route(self, path, method, tag, state):
        local = '_local' if state else ''
        router = 'swagger_server.controllers{}.{}_controller'.format(local, tag)
        self.conf['paths'][path][method]['x-swagger-router-controller'] = router

    def route(self):
        for controller in self.controllers:
            pathname = LOCAL.format(self.repo_path, self.repo, controller)
            if Path(pathname).is_file():
                with open(pathname) as io:
                    text = io.read()
            else:
                text = ''
            for fn, pth, method, tag in self.controllers[controller]:
                state = ('\ndef '+fn+'(') in text
                self.update_route(pth, method, tag, state)
        self.save()


if __name__ == '__main__':
    if len(argv) < 2:
        usage('insufficient parameters')

    import configparser

    config = configparser.ConfigParser()
    config.read('config.ini')

    api = YAML_API(config)
    api.open(argv[1])
    api.load_tags()
    api.load_controllers()

    if len(argv) == 2:
        api.check_codegen()
        exit(0)

    if argv[2] == 'status':
        api.status()
        exit(0)

    if argv[2] == 'route':
        api.route()
        exit(0)

    if argv[2] == 'list':
        api.list()
        exit(0)

    if len(argv) < 4:
        usage('insufficient parameters')

    if argv[2] == 'implement':
        api.implement(argv[3])
        api = YAML_API(config)
        api.open(argv[1])
        api.load_tags()
        api.load_controllers()
        api.route()
        exit(0)

    usage('unrecognised option')
    exit(0)
