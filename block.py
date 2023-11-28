from libs.importer import require
import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.walk import Block


require('__all__', globals())


reach = Player.getReach()
block = Player.rayTraceBlock(reach, True)

if block is None:
    pos = Player.getPlayer().getPos()
    pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
else:
    pos = block.getBlockPos()
    pos = [pos.getX(), pos.getY(), pos.getZ()]

block = Block.getBlock(pos)
# block = block.BlockDataHelper()

Chat.log(block.id)
Chat.log(block.pos)
Chat.log(f'isAir: {block.isAir}')
Chat.log(f'isLiquid: {block.isLiquid}')
Chat.log(f'isOpaque: {block.isOpaque}')

# Chat.log(block.getBlockStateHelper().isOpaque())

