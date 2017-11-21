import urllib2
import json
import ConfigParser
import os
import sys


class PropertyDto(object):
    key = ''
    value = ''
    type = ''
    common = False
    pass


class SnapshotDto(object):
    id = ''
    createdTime = ''
    applicationId = ''
    current = False
    properties = []
    pass


class Agent(object):
    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def getRemoteProperties(self, applicationId, environment):
        url = self.baseUrl + '/snapshot/get-current'
        body = {
            'env': environment,
            'systemAlias': applicationId
        }
        request = urllib2.Request(url, json.dumps(body))
        request.add_header('Content-Type', 'application/json')
        request.add_header('snapshot-password',
                           '5e05773e-4359-40e3-9cbf-fc0333846aa2')
        request.get_method = lambda: 'POST'

        try:
            response = urllib2.urlopen(request)
        except Exception:
            raise Exception('Failed to get remote properties.')

        snapshot = SnapshotDto()
        data = json.loads(response.read(), 'utf-8')
        if data['code'] == 0 and data['data'] != None and data['data']['properties'] != None:
            properties = []
            for i, element in enumerate(data['data']['properties']):
                property = PropertyDto()
                property.__dict__ = element
                properties.append(property)
            snapshot.__dict__ = data['data']
            snapshot.properties = properties
        else:
            raise Exception('Failed to get remote properties.')
        return snapshot


class EnvironmentVariables(object):
    applicationId = ''
    configCenterUrl = ''
    environment = ''

    def __init__(self):
        variables = os.environ
        self.applicationId = variables.get('systemAlias')
        self.configCenterUrl = variables.get('CONFIGURL')
        self.environment = variables.get('CONFIGENV')


class ConfigFileBuilder(object):
    configFilePath = ''
    configParser = ConfigParser.ConfigParser()

    def __init__(self, configFilePath):
        self.configFilePath = configFilePath

        if os.path.exists(self.configFilePath):
            os.remove(configFilePath)
        file = open(configFilePath, 'w')
        file.close()

    def build(self, types):
        if types != None:
            for type in types:
                if not self.configParser.has_section(type):
                    self.configParser.add_section(type)
                keyValues = types[type]
                for key in keyValues:
                    self.configParser.set(type, key, keyValues[key])
        print self.configParser
        file = open(self.configFilePath, 'w')
        self.configParser.write(file)
        file.close()


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    configFilePath = './config.ini'

    # # read file
    # file = open(configFilePath)
    # while True:
    #     lines = file.readlines(1024)
    #     if not lines:
    #         break
    #     for i, element in enumerate(lines):
    #         print element

    # # read config file
    # configParser = ConfigParser.ConfigParser()
    # configParser.read(configFilePath)

    # # list sections
    # print configParser.sections()
    # # list 'application' section's config nodes
    # print configParser.options('application')
    # # list 'runtime' section's config nodes
    # print configParser.items('runtime')
    # # get 'runtime' section's 'host' config node
    # print configParser.get('runtime', 'host')
    # # get 'runtime' section's 'port' config node as int type
    # print configParser.getint('runtime', 'port')

    # if not configParser.has_section('zhang'):
    #     configParser.add_section('zhang')

    # configParser.set('zhang', 'runky', 'zhang')
    # configParser.set('zhang', 'maity', 'peng')
    # configParser.write(open(configFilePath, 'w'))

    environmentVariables = EnvironmentVariables()
    print environmentVariables.applicationId
    print environmentVariables.configCenterUrl
    print environmentVariables.environment

    agent = Agent('http://10.0.54.242:8080/service')
    snapshot = agent.getRemoteProperties('arch.config.test.ui', 'TEST')
    types = {}
    for i, element in enumerate(snapshot.properties):
        if not types.has_key(element.type):
            types[element.type] = {}
        types[element.type][element.key] = element.value

    configFileBuilder = ConfigFileBuilder(configFilePath)
    configFileBuilder.build(types)
