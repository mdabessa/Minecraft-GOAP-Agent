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


start = Player.getPlayer().getPos()
start = [int(start.x), int(start.y), int(start.z)]

range_ = [25, 5, 25]

# end = [10**10, 0, 10**10]
# end = Calc.pointOnLine(start, end, 50)
# end1 = [end[0] + 10, -64, end[2] + 10]
# end2 = [end[0] - 10, 320, end[2] - 10]
# region = Region(end1, end2)

# walk = Walk(start, region)
# Chat.log(walk.getConfig())

from itertools import product

for x, y, z in product(range(-range_[0], range_[0]), range(-range_[1], range_[1]), range(-range_[2], range_[2])):
    pos = [start[0] + x, start[1] + y, start[2] + z]
    block = Block.getBlock(pos)    
    if block.id == 'minecraft:gray_wool':
        block_ = Block.getBlock([pos[0], pos[1] - 1, pos[2]])
        if block_.id == 'minecraft:gray_wool':
            Chat.say(f'/setblock {pos[0]} {pos[1]} {pos[2]} minecraft:barrier')