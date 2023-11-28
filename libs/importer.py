# This file is used to import libraries from the libs folder.
# The libs need to be imported with exec() to be able to use the JsMacrosAC classes.

import os

# Avoid importing the same library twice and circular imports
LIBS = {}
LIBS_PATH = os.path.join(os.getcwd(), 'config', 'jsMacros', 'Macros', 'libs')

def require(lib: str, __globals):
    """Import a library from the libs folder."""
    if lib in LIBS:
        return
    
    _lib = lib.split('.')
    name = _lib[-1]
    path = os.path.join(LIBS_PATH, *_lib[:-1])
    file = os.path.join(path, name + '.py')

    assert os.path.exists(file), f'Library [{lib}]({file}) does not exist.'

    with open(file, 'r') as f:
        exec(f.read(), __globals)
    
    
    LIBS[lib] = file

