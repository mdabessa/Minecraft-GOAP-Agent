from libs.importer import require, LIBS
import time

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style


delay = 0.8
controller = GlobalVars.getBoolean("forward")

if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("forward")

Logger.print(f'[Forward] script {"enabled" if controller else "disabled"}!')

while controller:
    controller = GlobalVars.getBoolean("forward")
    if not controller: break
    
    KeyBind.key('key.keyboard.w', True)
    Client.waitTick(1)

KeyBind.key('key.keyboard.w', False)

if controller:
    GlobalVars.toggleBoolean("forward")    
