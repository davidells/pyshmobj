#!/usr/bin/env python

import shmobj
from shmobj import SHMLST, SHMINT

# In normal local memory Python programs, creation and deletion of variables
# is automatic. The garbage collector automatically deletes a variable when
# no more references point to it. 
# 
# For example, in the following code, we declare a variable and a list containing
# the variable (or a reference to the variable, that is).
local_int = 10
local_list = [local_int]

# Now if we call a del(local_int) to delete the *reference* local_int, the *value*
# of local_int lives on, because local_list still points to it.
#
# So the following print statement should show local_list = [10]
del(local_int)
print 'local_list = %s' % local_list

# This is all good and fine, since in the local memory paradigm, when no more
# local references point to the variable, it should be deleted. However, in
# a shared memory paradigm, when all the local references to a shared variable
# have been deleted in a process, we *don't* want it to be automatically removed
# by the garbage collector, because some other process may have references to it.

# Instead, we are explicitly in charge of deleting shared memory variables
# by using delete calls.
shared_int = SHMINT(10)
shared_int.delete()

# So we must define different semantics for local references pointing to 
# deleted shared memory variables, since when we delete shared_int, the variable
# is truly gone. In this case, a reference (stored in shared memory) stored
# in a list (also in shared memory) still exists, but now returns the Python
# None object.

# So the following print statement should show shared_list = [None]
shared_int = SHMINT(10)
shared_list = SHMLST([shared_int])
shared_int.delete()
print 'shared_list = %s' % shared_list

# Note that this also means that shared_list still has a length of 1.
print 'len(shared_list) = %d' % len(shared_list)

# We must still delete the reference from the list to free the shared
# memory used for it. We do this with the delitem call, which we must
# explicitly call for the same reasons as stated above for an explicit delete.
# The delitem call also takes a 'shallow' parameter that acts just as the
# one in delete. By default it is not shallow, and will truly delete the item.
shared_list.delitem(0)

# For lists and dictionaries, the delete call takes an optional named
# parameter 'shallow' that will only delete the list and it's references,
# but not the actual variables. By default, the delete calls are not shallow,
# meaning every variable and sublist or subdictionary is also deleted recursively.
a, b, c = SHMINT(1), SHMINT(2), SHMINT(3)
for x in [a, b, c]: shared_list.append(x)
print 'shared_list = %s' % shared_list

# You can check the amount of memory available to you (in bytes)
# at any time using the freecount method in the shmobj module.
print 'freecount = %d' % shmobj.freecount()

# So now let's say we (deep) delete shared_list. We should then see a
# higher amount of available shared mem.
shared_list.delete()
print 'freecount after shared_list.delete() = %d' % shmobj.freecount()

# Again, we see that a different local reference pointing to a 
# deleted shared memory value will return the python None object
print 'a = %s' % a

# However, if we explicitly call delete using a reference to a variable
# and try to access it using that reference, shmobj throws an Exception.
a = SHMINT(99)
a.delete()
try: print 'a = %s' % a
except Exception, e: print 'Exception: %s' % e
