from libs.importer import require, LIBS
import time

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style


delay = 0.8
controller = GlobalVars.getBoolean("weather")

if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("weather")

Logger.print(f'[Weather] script {"enabled" if controller else "disabled"}!')

while controller:
    controller = GlobalVars.getBoolean("weather")
    if not controller: break
    
    wheater = World.isThundering()

    if wheater:
        Logger.print("It's thundering!")
        World.playSound("entity.experience_orb.pickup", 1, 1)


    Client.waitTick(5)


if controller:
    GlobalVars.toggleBoolean("weather")    
