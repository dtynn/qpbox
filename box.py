#coding=utf-8
from bucket import QBucket
import json
import logging
import os


logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)1.1s %(asctime)1.19s %(module)s:%(lineno)d] %(message)s')


class QPBoxError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, "%s" % (message,))


class QPBox(object):
    def __init__(self):
        self.initApp()
        self.initialize()
        return

    def initialize(self):
        return

    def initApp(self):
        self.initAppDir()
        self.initAppConf()
        self.initAppHistory()
        self.confReader()
        self.logReader()

        targetDir = self.confGet('target_dir', None)
        self.initDataDir(targetDir)

        bucket = self.confGet('bucket')
        domain = self.confGet('domain')
        accessKey = self.confGet('access_key')
        secretKey = self.confGet('secret_key')
        if not (bucket and domain and accessKey and secretKey):
            raise QPBoxError('invalid config file')
        self.qBucket = QBucket(bucket, domain, accessKey, secretKey)
        return

    def initAppDir(self):
        self.appDir = os.path.join(os.environ['HOME'], '.qpbox')
        try:
            os.makedirs(self.appDir, 0666)
            logging.info('app directory initialized')
        except OSError as e:
            logging.debug(e)
        return

    def initDataDir(self, target=None):
        if target:
            self.dataDir = os.path.abspath(target)
        else:
            self.dataDir = os.path.join(self.appDir, 'data')
        return

    def initAppHistory(self):
        self.logFile = os.path.join(self.appDir, 'history.log')
        try:
            os.mknod(self.logFile)
            logging.info('log file created')
        except OSError as e:
            logging.debug(e)
        return

    def initAppConf(self):
        self.confFile = os.path.join(self.appDir, 'qpbox.conf')
        try:
            os.mknod(self.confFile)
            logging.info('config file created')
        except OSError as e:
            logging.debug(e)
        return

    def confReader(self):
        try:
            with open(self.confFile, 'r') as f:
                data = f.read()
                data = data.replace('\r', '').replace('\n', '')
                self.confData = json.loads(data)
                logging.info('config file read')
        except Exception as e:
            raise QPBoxError(e)
        return

    def confGet(self, confKey, default=''):
        return str(self.confData.get(confKey, default))

    def logReader(self):
        try:
            logData = dict()
            with open(self.logFile, 'r') as f:
                for line in f:
                    fKey, fHash = line.rstrip('\n').split()
                    logData[fKey] = fHash
                self.logData = logData
                logging.info('log file read')
        except Exception as e:
            raise QPBoxError(e)
        return

    def syncFromCloud(self):
        diffItems = set(self.cloudGetList().items()) - set(self.localGetList().items())
        diffKeys = map(lambda x: x[0], diffItems)
        self.cloudGetFiles(diffKeys)
        return

    def localGetList(self):
        return self.logData

    def cloudGetList(self):
        return self.qBucket.listAll()

    def cloudGetFiles(self, keys):
        logging.info('updating %d file(s)' % (len(keys),))
        ignoredCt = 0
        for key in keys:
            fPath = self.utilMakeFIlePath(key)
            if fPath is not None:
                self.qBucket.getFile(key, fPath)
            else:
                ignoredCt += 1
        if ignoredCt > 0:
            logging.info('updated: ignored %d file(s) with invalid key' % (ignoredCt,))
        else:
            logging.info('updated: success')
        return

    def utilKeyValidation(self, key):
        if key.startswith('/') or key.endswith('/') or key.strip() == '':
            return
        return self.utilMakeFIlePath(key)

    def utilMakeFIlePath(self, key):
        fPath = os.path.join(self.dataDir, key)
        fDir = os.path.dirname(fPath)
        try:
            os.makedirs(fDir)
        except OSError as e:
            logging.debug(e)
        return fPath