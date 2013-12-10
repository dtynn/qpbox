#coding=utf-8
from qiniu import conf as qConf, rs as qRs, io as qIo, resumable_io as qRIo, rsf as qRsf
import logging
import os
import urllib


def utilItem2Str(item):
    rsKey = item['key'].encode('utf8')
    rsHash = str(item['hash'])
    #fsize = item['fsize']
    #mimeType = str(item['mimeType'])
    #putTime = item['putTime']
    #return '%s %s %d %s %d' % (fkey, fhash, fsize, mimeType, putTime)
    return '%s %s' % (rsKey, rsHash)


class QBucketError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, "%s" % (message,))


class QBucket(object):
    def __init__(self, bucket, domain, accessKey, secretKey):
        if not (bucket and domain and accessKey and secretKey):
            raise QBucketError('')

        self.bucket = bucket
        self.domain = domain
        self.accessKey = accessKey
        self.secretKey = secretKey
        qConf.ACCESS_KEY = accessKey
        qConf.SECRET_KEY = secretKey

        self._urlopen = urllib.URLopener()

        self.initialize()
        return

    def initialize(self):
        return

    def listAll(self):
        client = qRsf.Client()
        itemList = []
        marker = 'begin'
        while marker:
            current_m = marker if marker != 'begin' else ''
            ret, err = client.list_prefix(self.bucket, prefix='', limit=1000, marker=current_m)
            if err and err != 'EOF':
                raise QBucketError('Error to get list use marker: %s' % (current_m,))
            itemList += ret['items']
            marker = ret.get('marker')
        items = dict()
        for i in itemList:
            items[i['key'].encode('utf8')] = str(i['hash'])
        return items

    def getFile(self, key, localPath):
        url = 'http://%s/%s' % (self.domain, urllib.quote(key))
        logging.debug('downloading: %s' % (url,))
        try:
            self._urlopen.retrieve(url, localPath)
            logging.debug('downloaded: %s' % (url,))
        except Exception as e:
            logging.warning('failed to download: Domain:%s ; Key:%s ; Exception:%s'
                            % (self.domain, key, e))
        return

    def putFile(self, key, localFile, mimeType=None):
        putPolicy = qRs.PutPolicy('%s:%s' % (self.bucket, key))
        uptoken = putPolicy.token()
        putExtra = qIo.PutExtra()
        if mimeType is not None:
            putExtra.mime_type = '%s' % (mimeType,)

        statInfo = os.stat(localFile)
        fsize = statInfo.st_size
        ret, err = qIo.put_file(uptoken, key, localFile, putExtra)
        return ret, err
