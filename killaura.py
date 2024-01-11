from libs.importer import require, LIBS
import time
import math

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.walk import Walk, Node, Block
    from libs.scripts import Script
    from libs.gathering.wood import Wood
    from libs.inventory import Inv
    from libs.explorer import Explorer
    from libs.actions import Action
    from libs.craft import Craft
    from libs.test import Test, getEnvironment


# end = [10**10, 0, 10**10]
# end = Calc.pointOnLine(start, end, 50)
# end1 = [end[0] + 10, -64, end[2] + 10]
# end2 = [end[0] - 10, 320, end[2] - 10]
# region = Region(end1, end2)

# walk = Walk(start, region)
# Chat.log(walk.getConfig())

# start = Player.getPlayer().getPos()
# start = [int(start.x), int(start.y), int(start.z)]

# range_ = [25, 5, 25]


# raise Exception('This script is not working yet!')

controller = GlobalVars.getBoolean("killaura")
if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("killaura")
Chat.log(f'[KillAura] script {"enabled" if controller else "disabled"}!')


while controller:
    controller = GlobalVars.getBoolean("killaura")
    if not controller: break

    player = Player.getPlayer()
    pos = player.getPos()
    pos = [pos.x, pos.y, pos.z]
    # slot = 

    entities = World.getEntities()
    entities = [
        entity for entity in entities
        if entity.isAlive()
        and entity.getType() != 'minecraft:player'
        and entity.getType() != 'minecraft:item'
        and entity.getType() != 'minecraft:experience_orb'
        and Calc.distance(pos, [entity.getPos().x, entity.getPos().y, entity.getPos().z]) < 4
    ]
    entities.sort(key=lambda x: Calc.distance(pos, [x.getPos().x, x.getPos().y, x.getPos().z]))

    if len(entities) == 0:
        continue

    for entity in entities:
        pos_ = [entity.getPos().x, entity.getPos().y, entity.getPos().z]

        reach = Calc.distance(pos, pos_)
        block = Player.rayTraceBlock(reach, False)
        if block is not None: continue

        Chat.log(f'[KillAura] Attacking {entity.getName()} - {entity.getType()}')
        Player.getPlayer().lookAt(pos_[0], pos_[1], pos_[2])
        Client.waitTick(1)
        player.attack()
        time.sleep(0.8)
        break


if controller:
    GlobalVars.toggleBoolean("killaura")    
