#coding=utf-8
from bucket import QBucket
import logging
import os
import urllib


logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)1.1s %(asctime)1.19s %(module)s:%(lineno)d] %(message)s')


class QPBox(object):
    def __init__(self, targetDir, bucket, domain, accessKey, secretKey):
        self.qBucket = QBucket(bucket, domain, accessKey, secretKey)
        self.initialize()
        self.targetDir = targetDir
        self.appDir = os.path.join(os.environ['HOME'], '.qpbox')
        self.historyFile = os.path.join(self.appDir, 'history.log')
        return

    def initialize(self):
        return

    def run(self):
        #获取本地历史
        self.sync2local()
        return

    def sync2local(self):
        localItems = self.getLocalHistory()
        cloudItems = self.getCloudHistory()
        diff = set(cloudItems.items()) - set(localItems.items())
        diffKeys = map(lambda x: x[0], diff)
        self.getCloudFiles(diffKeys)
        return

    def getLocalHistory(self):
        try:
            with open(self.historyFile, 'r') as f:
                content = f.read()
        except IOError:
            self.initLocalHistory()
            return dict()
        itemList = content.split('\n')
        items = dict()
        for item in itemList:
            if item:
                rsKey, rsHash = item.split()
                items[rsKey] = rsHash
        return items

    def initLocalHistory(self):
        if not os.path.exists(self.appDir):
            logging.info('creating app dir')
            os.makedirs(self.appDir, 0666)
        with open(self.historyFile, 'w') as f:
            f.close()
        logging.info('File: %s initialized' % (self.historyFile,))
        return

    def getCloudHistory(self):
        return self.qBucket.listAll()

    def getCloudFiles(self, keys):
        logging.info('updating %d file(s) from cloud' % (len(keys),))
        ignoreCt = 0
        for key in keys:
            fPath = self.makeFilePath(key)
            if fPath is None:
                ignoreCt += 1
            else:
                pass
        return

    def makeFilePath(self, key):
        if self.validKey(key) is False:
            logging.debug('invalid key: %s' % (key,))
            return
        fPath = os.path.join(self.targetDir, key)
        fDir = os.path.dirname(fPath)
        try:
            os.makedirs(fDir, 0666)
        except Exception as e:
            logging.debug(e)
        return fPath

    def validKey(self, key):
        if key.startswith('/') or key.endswith('/') or key.strip() == '':
            return False
        return True