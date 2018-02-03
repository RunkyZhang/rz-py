import urllib2
import json
import ConfigParser
import os
import sys
import platform


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


class ConfigCenterAgent(object):
    def __init__(self, baseUrl):
        if baseUrl == None:
            raise Exception('The baseUrl is null.')

        self.baseUrl = baseUrl

    def getRemoteProperties(self, applicationId, environment):
        if applicationId == None:
            raise Exception('The applicationId is null.')
        if environment == None:
            raise Exception('The environment is null.')

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
        response = urllib2.urlopen(request)

        snapshot = SnapshotDto()
        data = json.loads(response.read(), 'utf-8')
        if data['code'] == 0:
            properties = []
            if data['data'] != None and data['data']['properties'] != None:
                for i, element in enumerate(data['data']['properties']):
                    property = PropertyDto()
                    property.__dict__ = element
                    properties.append(property)
                snapshot.__dict__ = data['data']
            snapshot.properties = properties
        elif data['code'] == -13003:
            snapshot.properties = []
        else:
            raise Exception(
                'Failed to get remote properties, message: ' + data['message'] + '.')
        return snapshot


class EnvironmentVariables(object):
    applicationId = ''
    configCenterBaseUrl = ''
    environment = ''

    def __init__(self):
        self.applicationId = os.environ.get('systemAlias')
        if (self.applicationId == None or self.applicationId == '') and 2 < len(sys.argv):
            self.applicationId = sys.argv[2]
        self.configCenterBaseUrl = os.environ.get('CONFIGURL')
        if (self.configCenterBaseUrl == None or self.configCenterBaseUrl == '') and 3 < len(sys.argv):
            self.configCenterBaseUrl = sys.argv[3]
        self.environment = os.environ.get('CONFIGENV')
        if self.environment == None or self.environment == '':
            if 4 < len(sys.argv):
                self.environment = sys.argv[4]
                if platform.system() == 'Windows' and (self.environment == 'PRD' or self.environment == '40'):
                    self.environment = 'TEST'
            else:
                self.environment = 'TEST'


class ConfigFileBuilder(object):
    configFilePath = ''
    configParser = ConfigParser.ConfigParser()

    def __init__(self, configFilePath):
        if configFilePath == None or configFilePath == '':
            raise Exception('The configFilePath is null.')

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
        file = open(self.configFilePath, 'w')
        self.configParser.write(file)
        file.close()


class Application(object):
    configFilePath = ''
    configFileName = 'config.ini'

    def __init__(self):
        if 1 < len(sys.argv):
            self.configFilePath = sys.argv[1]

        if self.configFilePath == None or self.configFilePath == '':
            raise Exception('Failed to get configFilePath from argv[1].')

        if not self.configFilePath.endswith('/'):
            self.configFilePath += '/'

    def run(self):
        environmentVariables = EnvironmentVariables()
        if environmentVariables.applicationId == None or environmentVariables.applicationId == '':
            raise Exception(
                'Failed to load applicationId from environment variables.')
        if environmentVariables.configCenterBaseUrl == None or environmentVariables.configCenterBaseUrl == '':
            raise Exception(
                'Failed to load configCenterBaseUrl from environment variables.')
        if environmentVariables.environment == None or environmentVariables.environment == '':
            raise Exception(
                'Failed to load from environment environment variables.')

        print 'applicationId: %s, environment: %s, configCenterBaseUrl: %s configFilePath: %s' \
            % (environmentVariables.applicationId, environmentVariables.environment, environmentVariables.configCenterBaseUrl, self.configFilePath)

        agent = ConfigCenterAgent(environmentVariables.configCenterBaseUrl)
        snapshot = agent.getRemoteProperties(
            environmentVariables.applicationId, environmentVariables.environment)
        types = {}
        for i, element in enumerate(snapshot.properties):
            if not types.has_key(element.type):
                types[element.type] = {}
            types[element.type][element.key] = element.value

        configFileBuilder = ConfigFileBuilder(
            self.configFilePath + self.configFileName)
        configFileBuilder.build(types)


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    try:
        Application().run()
        print 'Success to generate config file.'
        sys.exit(0)
    except Exception as e:
        print e
        sys.exit(1)
