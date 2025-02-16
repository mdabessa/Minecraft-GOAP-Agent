from libs.importer import require, LIBS
import time

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style


delay = 0.8
controller = GlobalVars.getBoolean("autoattack")

if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("autoattack")

Logger.print(f'[AutoAttack] script {"enabled" if controller else "disabled"}!')

while controller:
    controller = GlobalVars.getBoolean("autoattack")
    if not controller: break

    player = Player.getPlayer()
    player.attack()
    Client.waitTick(1)
    time.sleep(delay)

if controller:
    GlobalVars.toggleBoolean("autoattack")    
