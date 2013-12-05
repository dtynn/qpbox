#coding=utf-8
from qiniu import conf as qConf, rs as qRs, io as qIo, resumable_io as qRIo, rsf as qRsf
import os


class QBucketError(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, "QBucket Error: %s" % (message,))


class QBucket(object):
    def __init__(self, bucket, accessKey, secretKey):
        if not (bucket and accessKey and secretKey):
            raise QBucketError('No accessKey or secretKey')

        self.bucket = bucket
        self.accessKey = accessKey
        self.secretKey = secretKey
        qConf.ACCESS_KEY = accessKey
        qConf.SECRET_KEY = secretKey

        self.initialize()
        return

    def initialize(self):
        return

    def fileListAll(self):
        client = qRsf.Client()
        key_list = []
        marker = 'begin'
        while marker:
            last_m = marker if marker != 'begin' else ''
            ret, err = client.list_prefix(self.bucket, prefix='', limit=1000, marker=last_m)
            #todo

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