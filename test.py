#coding=utf-8
from box import QPBox
from bucket import QBucket

a = 'iguImegxd6hbwF8J6ij2dlLIgycyU4thjg-xmu9q'
s = 'EXJInB-eR0nkOwFet9uwP89MNzSpNXVqBoSh1yBo'

b = 't-test-mirror'
d = '%s.u.qiniudn.com' % (b,)

box = QPBox('/home/dtynn/work/test/mysync', b, d, a, s)
box.run()


#bucket = QBucket(b, h, a, s)
#
#ilist, err = bucket.listAll()

#print ilist
#for i in ilist:
#    print i
