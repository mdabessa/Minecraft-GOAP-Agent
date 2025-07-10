from libs.importer import require, LIBS
import time

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.actions import Action
    from libs.walk import Block


controller = GlobalVars.getBoolean("concrete")

if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("concrete")

Logger.print(f'[AutoConcrete] script {"enabled" if controller else "disabled"}!')

player = Player.getPlayer()
pos = player.getPos()

block = Block.getLookAtBlock()
blockPos = [block.pos[0], block.pos[1]+1, block.pos[2]]
while controller:
    controller = GlobalVars.getBoolean("concrete")
    if not controller: break
    player = Player.getPlayer()

    if player.getPos() != pos:
        Logger.print("[AutoConcrete] Player moved, script disabled!")
        GlobalVars.toggleBoolean("concrete")
        break
    
    Action.placeBlock(blockPos, 'minecraft:concrete_powder', moveToPlace=False, exactId=False)
    Action.breakBlock(blockPos, safe=False)

    Client.waitTick()


if controller:
    GlobalVars.toggleBoolean("concrete")    
