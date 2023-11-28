# Import all modules in libs
# If importing in order and without circular imports, only need to import in the main file,
# otherwise import in all files that need to use the libs.
 
from libs.importer import require

# Fundamental libs, utils that don't depend on other libs
require('utils.calc', globals())
require('utils.dictionary', globals())

# Fundamental libs, just depend on JsMacrosAC or Utils
require('state', globals())
require('scripts', globals())
require('inventory', globals())
require('explorer', globals())

# Core libs, depend on fundamental libs
require('walk', globals())
require('actions', globals())
require('craft', globals())

# Macros libs (implement high level abstractions), depend on core libs
require('gathering.wood', globals())
require('gathering.miner', globals())

# Interface libs, depend on all other libs
require('test', globals())
require('commands', globals())
