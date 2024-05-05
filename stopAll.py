# Purpose: Stop all scripts, the script needs to have a listener to stop itself
# this script only triggers all the flags to the listeners to stop

from libs.importer import require

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.scripts import Script

require('scripts', globals())
require('utils.logger', globals())


len_ = len(Script.getScripts())

Logger.print(f'Stopping all scripts ({len_})')
Script.stopAllScripts()
