#!/usr/bin/env python

import os, sys, atexit, py2shmobj
import string, random

__ver__ = "0.9.1"

__all__ = ["SHMOBJ", "SHMNUM", "SHMINT","SHMDBL","SHMSTR","SHMLST","SHMDCT","SHMPTR"]

TYPEINT = 1
TYPEDBL = 2
TYPESTR = 3
TYPELST = 4
TYPEDCT = 5
TYPEPTR = 9  # not handling ptrs like others below; esp. not handled in lists

__shmtypes = [TYPEINT, TYPEDBL, TYPESTR, TYPELST, TYPEDCT, TYPEPTR]

class SHMOBJ(object):
    def __init__(self, arg, internal):
        self.addr = None
        if str(type(arg)) == "<type 'PyCObject'>"  and  internal:
            self.addr = arg
    def __del__(self):
        pass
    def __cmp__(self, obj):
        self.protect()
        if isinstance(obj, SHMOBJ):
            return py2shmobj.shmobj_equals(self.addr, obj.get_ptr())
        else:
            return cmp(self.val(), obj) == 0
    def __hash__(self):
        return hash(self.val())
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        self.protect()
        return str(self.val())
    def delete(self):
        self.protect()
        py2shmobj.shmobj_del(self.addr)
        self.addr = None
    def get_ptr(self):
        return self.addr
    def protect(self):
        if not self.addr:
            raise Exception("shared memory object no longer exists")
    def val(self):
        raise Exception("abstract method called")

class SHMNUM(SHMOBJ):
    def __init__(self, arg, internal):
       SHMOBJ.__init__(self, arg, internal)
    def __abs__(self,arg):
        return abs(self.val())
    def __add__(self,arg):
        return (self.val() + arg)
    def __sub__(self,arg):
        return (self.val() - arg)
    def __cmp__(self,arg):
        SHMOBJ.protect(self)
        if type(arg) in [SHMLST, SHMSTR, SHMDCT]:
            return -1
        return cmp(self.val(), arg)
    def __complex__(self):
        return complex(self.val())
    def __div__(self, arg):
        return self.val() / arg
    def __divmod__(self, arg):
        return divmod( self.val(), arg )
    def __float__(self):
        return float(self.val())
    def __int__(self):
        return int(self.val())
    def __long__(self):
        return long(self.val())
    def __mod__(self,arg):
        return (self.val() % arg)
    def __mul__(self,arg):
        return (self.val() * arg)
    def __rmul__(self,arg):
        return (self.val() * arg)
    def __radd__(self,arg):
        return self.__add__(arg)
    def __rsub__(self,arg):
        return arg.__sub__(self.val())
    def __rdivmod__(self, arg):
        return divmod(arg, float(self.val()))

class SHMINT(SHMNUM):
    def __init__(self,arg,internal=False):
        SHMNUM.__init__(self, arg, internal)
        if isinstance(arg,int):
            self.addr = py2shmobj.shmint_alloc()
            if self.addr is None:
                raise Exception('SHMINT allocation failed: out of memory')
            py2shmobj.shmint_set(self.addr,arg)
        elif self.addr is None:
            raise TypeError("invalid type %s assigned to SHMINT" % type(arg))
    def set(self,arg):
        SHMOBJ.protect(self)
        py2shmobj.shmint_set(self.addr,arg)
    def val(self):
        SHMOBJ.protect(self)
        return py2shmobj.shmint_get(self.addr)

class SHMDBL(SHMNUM):
    def __init__(self,arg,internal=False):
        SHMNUM.__init__(self, arg, internal)
        if type(arg) in [float, int, SHMINT, SHMDBL]:
            self.addr = py2shmobj.shmdbl_alloc()
            if self.addr is None:
                raise Exception('SHMDBL allocation failed: out of memory')
            if isinstance(arg,int):
                arg = float(arg)
            py2shmobj.shmdbl_set(self.addr,arg)
        elif self.addr is None:
            raise TypeError("invalid type %s assigned to SHMDBL" % type(arg))
    def set(self,arg):
        SHMOBJ.protect(self)
        if type(arg) in [float, int, SHMINT, SHMDBL]:
            py2shmobj.shmdbl_set(self.addr,arg)
        else:
            raise TypeError("invalid type %s assigned to SHMDBL" % type(arg))
    def val(self):
        SHMOBJ.protect(self)
        return py2shmobj.shmdbl_get(self.addr)

class SHMSTR(SHMOBJ):
    def __init__(self,arg,internal=False):
        SHMOBJ.__init__(self, arg, internal)
        if isinstance(arg,str):
            self.addr = py2shmobj.shmstr_alloc(len(arg))
            if self.addr is None:
                raise Exception('SHMSTR allocation failed: out of memory')
            py2shmobj.shmstr_set(self.addr,arg)
        elif self.addr is None:
            raise TypeError("invalid type %s assigned to SHMSTR" % type(arg))
    def __getattr__(self, arg):
        SHMOBJ.protect(self)
        return getattr(self.val(), arg)
    def __add__(self, arg):
        SHMOBJ.protect(self)
        return self.val().__add__(arg)
    def __contains__(self, arg):
        SHMOBJ.protect(self)
        return self.val().__contains__(arg)
    def __cmp__(self, arg):
        SHMOBJ.protect(self)
        if not type(arg) in [str, SHMSTR]:
            return cmp(self.__class__.__name__, \
                        arg.__class__.__name__)
        return cmp(str(self), str(arg))
    def __getitem__(self, arg):
        SHMOBJ.protect(self)
        return self.val().__getitem__(arg)
    def __getslice__(self, idx_a, idx_b):
        SHMOBJ.protect(self)
        return self.val().__getslice__(idx_a, idx_b)
    def __len__(self):
        SHMOBJ.protect(self)
        return len(self.val())
    def __mod__(self, arg):
        SHMOBJ.protect(self)
        return self.val().__mod__(arg)
    def __mul__(self, arg):
        SHMOBJ.protect(self)
        return self.val().__mul__(arg)
    def __repr__(self):
        SHMOBJ.protect(self)
        return "'%s'" % self.val()
    def __str__(self):
        SHMOBJ.protect(self)
        return self.val()
    def __radd__(self, arg):
        SHMOBJ.protect(self)
        return arg.__add__(self.val())
    def __rmod__(self, arg):
        SHMOBJ.protect(self)
        return arg.__mod__(self.val())
    def __rmul__(self, arg):
        SHMOBJ.protect(self)
        return arg.__mul__(self.val())
    def val(self):
        SHMOBJ.protect(self)
        return py2shmobj.shmstr_get(self.addr)

class SHMLST_ITER(object):
    def __init__(self, shmlist):
        self.list = shmlist.get_ptr()
        self.node = py2shmobj.shmlist_first(self.list)
    def __iter__(self):
        self.node = py2shmobj.shmlist_first(self.list)
        return self
    def next(self):
        if self.node:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(self.node)
            obj = typed_ptr(p,datatype)
            self.node = py2shmobj.shmlist_next(self.list, self.node)
            return obj
        else:
            raise StopIteration

class SHMLST_RITER(object):
    def __init__(self, shmlist):
        self.list = shmlist.get_ptr()
        self.node = py2shmobj.shmlist_last(self.list)
    def __iter__(self):
        self.node = py2shmobj.shmlist_last(self.list)
        return self
    def next(self):
        if self.node:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(self.node)
            obj = typed_ptr(p,datatype)
            self.node = py2shmobj.shmlist_prev(self.list, self.node)
            return obj
        else:
            raise StopIteration
        
class SHMLST(SHMOBJ):
    def __init__(self,larg,internal=False):
        SHMOBJ.__init__(self, larg, internal)
        if isinstance(larg,list):
            self.addr = py2shmobj.shmlist_init()
            if self.addr is None:
                raise Exception('SHMLST allocation failed: out of memory')
            for e in larg:
                if not isinstance(e, SHMOBJ):
                    raise TypeError("** invalid type being inserted in shmlist")
                ep = e.get_ptr()
                np = py2shmobj.shmlnode_alloc()
                (datatype, datalen) = get_type_and_len(e)
                py2shmobj.shmlnode_init(np,ep,datatype,datalen)
                py2shmobj.shmlist_append(self.addr,np)
        elif self.addr is None:
            raise TypeError("invalid type %s assigned to SHMLST" % type(arg))

    def __iter__(self):
        return SHMLST_ITER(self)

    def __reversed__(self):
        return SHMLST_RITER(self)

    def __contains__(self, item):
        SHMOBJ.protect(self)
        try:
            if(self.index(item) >= 0):
                return True
        except ValueError:
            return False

    def __getitem__(self,idx):
        SHMOBJ.protect(self)
        if idx < 0:
            idx += len(self)
        if idx < 0 or not type(idx) in [int, SHMINT]:
            raise IndexError
        np = py2shmobj.shmlist_getnode(self.addr, idx)
        if np:
            (ep,datatype,datalen) = py2shmobj.shmlnode_get(np)
            return typed_ptr(ep,datatype)
        else:
            raise IndexError

    def __getslice__(self,idx_a,idx_b):
        SHMOBJ.protect(self)
        slice = []

        if idx_b == sys.maxint:
            idx_b = len(self)

        if idx_a < 0:
            idx_a += len(self)
            if idx_a < 0:
                idx_a = 0
        if idx_a > len(self):
            idx_a = len(self)

        if idx_b < 0:
            idx_b += len(self)
            if idx_b < 0:
                idx_b = 0
        if idx_b > len(self):
            idx_b = len(self)

        if idx_b <= idx_a: 
            return slice

        if idx_a < 0 or idx_b < 0 or idx_a > len(self) or idx_b > len(self):
            raise IndexError

        i = idx_a
        np = py2shmobj.shmlist_getnode(self.addr, idx_a)
        while np and i < idx_b:
            (ep,datatype,datalen) = py2shmobj.shmlnode_get(np)
            slice.append(typed_ptr(ep,datatype))
            np = py2shmobj.shmlist_next(self.addr,np)
            i += 1
        if i < idx_b:
            raise IndexError
        return slice

    def __len__(self):
        SHMOBJ.protect(self)
        return py2shmobj.shmlist_count(self.addr)

    def __setitem__(self,idx,arg):
        SHMOBJ.protect(self)
        #### RMB: VERIFY THAT ARG IS ALREADY SHMOBJ
        if not isinstance(arg, SHMOBJ):
            raise TypeError("** invalid type being replaced in shmlist")
        datatype, datalen = get_type_and_len(arg)
        np = py2shmobj.shmlist_getnode(self.addr, idx)
        if np:
            ep = arg.get_ptr()
            py2shmobj.shmlnode_put(np,ep,datatype,datalen)
            return None
        else:
            raise IndexError

    def __add__(self, arg):
        SHMOBJ.protect(self)
        if not type(arg) in [list, SHMLST]:
            raise TypeError("unsupported operand type(s) for +: " +\
                            "'%s' and '%s'" % (type(self), type(arg)))
        if isinstance(arg, SHMLST):
            arg = list(arg)
        return self.val() + arg

    def __iadd__(self, arg):
        SHMOBJ.protect(self)
        if not type(arg) in [list, SHMLST]:
            raise TypeError("unsupported operand type(s) for +=: " +\
                            "'%s' and '%s'" % (type(self), type(arg)))
        for item in arg:
            self.append(item)
        return self
    
    def __cmp__(self, arg):
        SHMOBJ.protect(self)
        if not type(arg) in [list, SHMLST]:
            return cmp(self.__class__.__name__, \
                        arg.__class__.__name__)

        if not len(self) == len(arg):
            return cmp(len(self), len(arg))

        for i in range(0, len(arg)):
            rc = cmp(self[i], arg[i])
            if rc != 0:
                return rc
        return 0

    def append(self,arg):
        SHMOBJ.protect(self)
        return self.insert(len(self), arg)

    def count(self, arg):
        SHMOBJ.protect(self)
        count = 0
        np = py2shmobj.shmlist_first(self.addr)
        while np:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(np)
            obj = typed_ptr(p,datatype)
            if obj == arg:
                count += 1
            np = py2shmobj.shmlist_next(self.addr,np)
        return count

    def delete(self, shallow=False):
        SHMOBJ.protect(self)
        np = py2shmobj.shmlist_first(self.addr)
        while np:
            if not shallow:
                (p,datatype,datalen) = py2shmobj.shmlnode_get(np)
                if p:
                    val = typed_ptr(p,datatype)
                    if type(val) in [SHMLST, SHMDCT]:
                        val.delete(shallow=shallow)
                    elif isinstance(val, SHMOBJ):
                        val.delete()
            next = py2shmobj.shmlist_next(self.addr,np)
            py2shmobj.shmlist_remove(self.addr, np)
            py2shmobj.shmobj_del(np)
            np = next
        SHMOBJ.delete(self)

    def delitem(self, idx, shallow=False):
        SHMOBJ.protect(self)
        np = py2shmobj.shmlist_getnode(self.addr, idx)
        if not np:
            raise IndexError

        if not shallow:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(np)
            if p:
                obj = typed_ptr(p,datatype)
                if isinstance(obj, SHMLST): 
                    obj.delete(shallow=shallow)
                else:
                    obj.delete()

        py2shmobj.shmlist_remove(self.addr,np)
        py2shmobj.shmobj_del(np)

    def extend(self, arg):
        SHMOBJ.protect(self)
        for item in arg:
            self.append(item)

    def index(self, item, begIdx=0, endIdx=sys.maxint):
        SHMOBJ.protect(self)
        idx = 0
        np = py2shmobj.shmlist_getnode(self.addr, begIdx)
        while np and idx < endIdx:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(np)
            obj = typed_ptr(p,datatype)
            if obj == item:
                return idx
            np = py2shmobj.shmlist_next(self.addr,np)
            idx += 1
        raise ValueError

    def insert(self, idx, item):
        SHMOBJ.protect(self)
        mylen = len(self)
        if(idx < 0):
            idx += mylen
        if(idx < 0):
            idx = 0
        if(idx > mylen):
            idx = mylen

        if not isinstance(item, SHMOBJ):
            raise TypeError("cannot insert type '%s' into SHMLST" % type(item))
        datatype, datalen = get_type_and_len(item)
        ep = item.get_ptr()
        np = py2shmobj.shmlnode_alloc()
        if np is None:
            raise Exception('shmlnode_alloc failed: out of memory')
        py2shmobj.shmlnode_init(np,ep,datatype,datalen)
        py2shmobj.shmlist_insert(self.addr, idx, np)
        return None
        
        
    def pop(self, idx=-1):
        SHMOBJ.protect(self)
        if idx < 0:
            idx += len(self)
        if idx < 0:
            raise IndexError
        item = self[idx]
        self.delitem(idx, shallow=True)
        return item

    def sort(self, cmp=None, key=None, reverse=False):
        SHMOBJ.protect(self)
        local = self.val()
        local.sort(cmp=cmp,key=key,reverse=reverse)
        for i in range(len(self)):
            self.delitem(0, shallow=True)
            self.append(local[i])

    def remove(self, item):
        SHMOBJ.protect(self)
        np = py2shmobj.shmlist_first(self.addr)
        while np:
            (p,datatype,datalen) = py2shmobj.shmlnode_get(np)
            obj = typed_ptr(p,datatype)
            if obj == item:
                py2shmobj.shmlist_remove(self.addr, np)
                return None
            np = py2shmobj.shmlist_next(self.addr,np)

    def reverse(self):
        SHMOBJ.protect(self)
        local = self.val()
        local.reverse()
        for i in range(len(self)):
            self.delitem(0, shallow=True)
            self.append(local[i])
        
    def val(self):
        SHMOBJ.protect(self)
        return list(self)


class SHMDCT_ITER(object):
    def __init__(self, shmdict, type='keys'):
        self.dict = shmdict.get_ptr()
        self.node = py2shmobj.shmdict_first(self.dict)
        if type == 'values':
            self.__val = self.__value
        elif type == 'items':
            self.__val = self.__item
        else:
            self.__val = self.__key

    def __iter__(self):
        self.node = py2shmobj.shmdict_first(self.dict)
        return self

    def __key(self):
        kp = py2shmobj.shmdnode_getkey(self.node)
        #DE - for now we assume the key is always a SHMSTR
        key = SHMSTR(kp,internal=True)
        return key

    def __value(self):
        (p,datatype,datalen) = py2shmobj.shmdnode_get(self.node)
        obj = typed_ptr(p,datatype) 
        return obj

    def __item(self):
        return (self.__key(), self.__value())

    def next(self):
        if self.node:
            return_val = self.__val()
            self.node = py2shmobj.shmdict_next(self.dict, self.node)
            return return_val
        else:
            raise StopIteration

class SHMDCT(SHMOBJ):
    def __init__(self,arg,internal=False):
        SHMOBJ.__init__(self, arg, internal)
        if type(arg) in [dict, SHMDCT]:
            self.addr = py2shmobj.shmdict_init()
            for (k,e) in arg.items():
                e = arg[k]
                if not isinstance(k,SHMSTR):
                    raise TypeError("**error: keys may only be SHMSTR at this time")
                if not isinstance(e, SHMOBJ):
                    raise TypeError("** invalid type being inserted in shmdict")
                datatype, datalen = get_type_and_len(e)
                dnode = py2shmobj.shmdnode_alloc()
                if dnode is None:
                    raise Exception('shmdnode_alloc failed: out of memory')
                py2shmobj.shmdnode_init(dnode, e.get_ptr(), datatype, datalen)
                py2shmobj.shmdict_insert(self.addr, dnode, k.get_ptr())
        elif self.addr is None:
            raise TypeError("invalid type %s assigned to SHMDCT" % type(arg))

    def __cmp__(self, arg):
        SHMOBJ.protect(self)
        if not type(arg) in [dict, SHMDCT]:
            return cmp(self.__class__.__name__, \
                        arg.__class__.__name__)

        if not len(self) == len(arg):
            return cmp(len(self), len(arg))

        keys = sorted(self.keys())
        argkeys = sorted(arg.keys())

        if not keys == argkeys:
            return cmp(keys, argkeys)

        for key in keys:
            rc = cmp(self[key], arg[key])
            if rc != 0:
                return rc
        return 0

    def __contains__(self, key):
        SHMOBJ.protect(self)
        try:
            temp = self.__getitem__(key)
            return True
        except KeyError:
            return False
        except TypeError:
            return False

    def __getitem__(self,key):
        SHMOBJ.protect(self)
        if isinstance(key, SHMSTR):
            key = str(key)
        if not isinstance(key, str):
            raise TypeError("** error: SHMDCT.__getitem__ only takes SHMSTR or str for key")
        np = py2shmobj.shmdict_lookup(self.addr, key)
        if not np:
            raise KeyError(key)
        else:
            (ep,datatype,datalen) = py2shmobj.shmdnode_get(np)
            return typed_ptr(ep,datatype)

    def __iter__(self):
        return SHMDCT_ITER(self)

    def __len__(self):
        SHMOBJ.protect(self)
        return py2shmobj.shmdict_count(self.addr)

    def __setitem__(self,key,arg):
        SHMOBJ.protect(self)
        if not type(key) in [str, SHMSTR]:
            raise TypeError("** error: SHMDCT.__setitem__ only takes SHMSTR or str for key")
        if not isinstance(arg, SHMOBJ):
            raise TypeError("** invalid type being set in shmdict")
        datatype, datalen = get_type_and_len(arg)
        np = py2shmobj.shmdict_lookup(self.addr, str(key))
        if np:
            py2shmobj.shmdnode_put(np,arg.get_ptr(),datatype,datalen)
        else:
            if not isinstance(key, SHMSTR):
                raise TypeError("** error: SHMDCT.__setitem__ only takes SHMSTR when key is new")
            dnode = py2shmobj.shmdnode_alloc()
            if dnode is None:
                raise Exception('shmdnode_alloc failed: out of memory')
            py2shmobj.shmdnode_init(dnode, arg.get_ptr(), datatype, datalen)
            py2shmobj.shmdict_insert(self.addr, dnode, key.get_ptr())
            
    def clear(self, shallow=False):
        SHMOBJ.protect(self)
        np = py2shmobj.shmdict_first(self.addr)
        while np:
            (p,datatype,datalen) = py2shmobj.shmdnode_get(np)
            if not shallow:
                #DE - for now we assume the key is always a SHMSTR
                kp = py2shmobj.shmdnode_getkey(np)
                py2shmobj.shmobj_del(kp)
                val = typed_ptr(p,datatype)
                if type(val) in [SHMLST, SHMDCT]:
                    val.delete(shallow=shallow)
                elif isinstance(val, SHMOBJ):
                    val.delete()
            next = py2shmobj.shmdict_next(self.addr,np)
            py2shmobj.shmdict_remove(self.addr, np)
            py2shmobj.shmobj_del(np)
            np = next

    def copy(self):
        SHMOBJ.protect(self)
        return SHMDCT(self)
        
    def delete(self, shallow=False):
        SHMOBJ.protect(self)
        self.clear(shallow=shallow)
        SHMOBJ.delete(self)

    def get(self, key, defval=None):
        SHMOBJ.protect(self)
        try:
            return self.__getitem__(key)
        except KeyError:
            return defval

    def has_key(self, key):
        SHMOBJ.protect(self)
        return self.__contains__(key)

    def items(self):
        SHMOBJ.protect(self)
        return [x for x in self.iteritems()]

    def iteritems(self):
        SHMOBJ.protect(self)
        return SHMDCT_ITER(self, type='items')

    def iterkeys(self):
        SHMOBJ.protect(self)
        return SHMDCT_ITER(self, type='keys')

    def itervalues(self):
        SHMOBJ.protect(self)
        return SHMDCT_ITER(self, type='values')

    def keys(self):
        SHMOBJ.protect(self)
        return [x for x in self.iterkeys()]

    def pop(self, key, defval=None, deletekey=True):
        SHMOBJ.protect(self)
        if isinstance(key, SHMSTR):
            key = str(key)
        if not isinstance(key, str):
            raise TypeError("** error: SHMDCT.pop only takes SHMSTR or str for key")
        np = py2shmobj.shmdict_lookup(self.addr, key)
        if np:
            kp = py2shmobj.shmdnode_getkey(np)
            (ep,datatype,datalen) = py2shmobj.shmdnode_get(np)
            py2shmobj.shmdict_remove(self.addr, np)
            py2shmobj.shmobj_del(np)
            if deletekey == True:
                py2shmobj.shmobj_del(kp)
            return typed_ptr(ep,datatype)
        if defval:
            return defval
        else:
            raise KeyError(key)

    def popitem(self):
        SHMOBJ.protect(self)
        np = py2shmobj.shmdict_first(self.addr)
        if np:
            kp = py2shmobj.shmdnode_getkey(np)
            key = SHMSTR(kp,internal=True)
            val = self.pop(key, deletekey=False)
            return (key, val)
        else:
            raise KeyError('popitem(): SHMDCT is empty')

    def setdefault(self, key, val):
        try:
            return self[key]
        except KeyError:
            self[key] = val
            return self[key]
        
    def values(self):
        SHMOBJ.protect(self)
        return [x for x in self.itervalues()]

    def val(self):
        SHMOBJ.protect(self)
        return dict(self)


class SHMPTR(SHMOBJ):
    def __init__(self,arg):
        SHMOBJ.__init__(self, arg, internal=False)
        self.addr = py2shmobj.shmptr_alloc()
        if self.addr is None:
            raise Exception('SHMPTR allocation failed: out of memory')
        if arg:
            py2shmobj.shmptr_put(self.addr,arg)
    def set(self,arg):
        SHMOBJ.protect(self)
        py2shmobj.shmptr_set(self.addr,arg)
    def get(self):
        SHMOBJ.protect(self)
        ptr = py2shmobj.shmptr_get(self.addr)
        return ptr

class semaphore(object):
    created_sems = []
    def __init__(self,val=1,name=''):
        if name == '':
            name = 'pyshmobj_%d_sem_%s' \
                   % (os.getpid(), self.__random_chars(10))
        self.name = name
        self.addr = py2shmobj.shmsem_open(name,val)
        semaphore.created_sems.append(self)
    def wait(self):
        py2shmobj.shmsem_wait(self.addr)
    def post(self):
        py2shmobj.shmsem_post(self.addr)
    def close(self):
        py2shmobj.shmsem_close(self.addr)
    def unlink(self):
        py2shmobj.shmsem_unlink(self.name)
    def __random_chars(self, numchars):
        rv = ''
        max_index = len(string.ascii_letters) - 1
        for i in range(numchars):
            rv += string.ascii_letters[ random.randint(0,max_index) ]
        return rv

class barrier(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.joined = SHMINT(0)
        self.mutex_sem = semaphore(val=1)
        self.barrier_sem = semaphore(val=0)
        self.signaler_sem = semaphore(val=0)

    def delete(self):
        self.joined.delete()

    def join(self):
        m = self.mutex_sem
        b = self.barrier_sem
        s = self.signaler_sem
        m.wait()
        self.joined.set(self.joined + 1)
        if self.joined == self.capacity:
            #print '%s: breaking barrier' % os.getpid()
            self.joined.set(0)
            for j in range(0, self.capacity-1):
                b.post()
                s.wait()
            m.post()
        else:
            m.post()
            #print '%s: joining barrier' % os.getpid()
            b.wait()
            s.post()
            m.wait()
            m.post()
        #print '%s: leaving barrier' % os.getpid()
        

def get_type_and_len(ptr):
    if isinstance(ptr,SHMINT):
        datatype = TYPEINT
        datalen = 0
    elif isinstance(ptr,SHMDBL):
        datatype = TYPEDBL
        datalen = 0
    elif isinstance(ptr,SHMSTR):
        datatype = TYPESTR
        datalen = len(ptr)
    elif isinstance(ptr,SHMLST):
        datatype = TYPELST
        datalen = 0
    elif isinstance(ptr,SHMDCT):
        datatype = TYPEDCT
        datalen = 0
    else:
        raise Exception("** error: tried to find type and len of non shmobj class")
    return (datatype, datalen)

def typed_ptr(ptr, datatype):
    if datatype == TYPEINT:
        val = SHMINT(ptr,internal=True)
    elif datatype == TYPEDBL:
        val = SHMDBL(ptr,internal=True)
    elif datatype == TYPESTR:
        val = SHMSTR(ptr,internal=True)
    elif datatype == TYPELST:
        val = SHMLST(ptr,internal=True)
    elif datatype == TYPEDCT:
        val = SHMDCT(ptr,internal=True)
    elif datatype == 0:
        val = None
    else:
        print "** NOT YET HANDLING TYPE", datatype
        val = None
    return val

def add_shmem_pages(page_count):
    #DE: Note this call should not be made AFTER forking
    return py2shmobj.shmobj_add_shmem_pages(page_count)

def __cleanup():
    #close and unlink all named semaphores
    for sem in semaphore.created_sems:
        sem.close()
        sem.unlink()
    #call backend cleanup
    py2shmobj.shmobj_cleanup()

#Debug functions
def freecount():
    return py2shmobj.shmobj_freecount()
def print_freelist():
    return py2shmobj.shmobj_print_freelist()


atexit.register(__cleanup)

