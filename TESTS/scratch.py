#!/usr/bin/python -i

import shmobj

shmobj.add_shmem_pages(10000)
print 'init mem', shmobj.freecount()

ll = []
ld = {}
shml = shmobj.SHMLST([])
shmd = shmobj.SHMDCT({})

for i in range(64):

    ll.append(i)
    ld[str(i)] = i

    shml.append( shmobj.SHMINT(i) )
    shmd[shmobj.SHMSTR(str(i))] = shmobj.SHMINT(i)


a = shmobj.SHMINT(20)
b = shmobj.SHMDBL(34.4)
c = shmobj.SHMDBL(18.2)
shmstr = shmobj.SHMSTR('Shared Memory!!!')
lstr = 'Local Memory!!!'

shmstr = shmobj.SHMSTR("Hello World!")
lstr = "Hello World!"

shml.append(a)
print 'shml.index(a) = %d' % shml.index(a)
shml.append(b)
print 'appended b, len(shml) = %d' % len(shml)
print 'shml.index(3) = %d' % shml.index(3)
print 'shml.index(b) = %d' % shml.index(b)
