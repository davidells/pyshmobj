
from distutils.core import setup, Extension

shmobj_module = Extension( "py2shmobj",
                           library_dirs = ['/usr/lib'],
                           sources=["py2shmobj.c", 
                                        "xxshmalloc.c",
                                        "list.c", 
                                        "dict.c"] )

setup(name="py2shmobj", version="0.9.1", 
      ext_modules=[shmobj_module])

