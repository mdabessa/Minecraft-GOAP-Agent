from libs.importer import require
import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.walk import Block


require('__all__', globals())


reach = Player.getReach()
block = Player.rayTraceBlock(reach, True)
pitch = Player.getPlayer().getPitch()
yaw = Player.getPlayer().getYaw()
pos = Player.getPlayer().getPos()
pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
blockP = Block.getBlock(pos)

if block is None:
    block = blockP
else:
    pos = block.getBlockPos()
    pos = [pos.getX(), pos.getY(), pos.getZ()]
    block = Block.getBlock(pos)


Logger.print(Style.GOLD + "Block Info")
Logger.print(block.id)
Logger.print(block.pos)
Logger.print(f'Hardness: {block.blockState.getHardness()}')
Logger.print(f'isAir: {block.isAir}')
Logger.print(f'isLiquid: {block.isLiquid}')
Logger.print(f'isOpaque: {block.isOpaque}')
Logger.print(f'isSolid: {block.isSolid}')

Logger.print(Style.GOLD + "Player Info")
Logger.print('Pitch: ' + str(pitch))
Logger.print('Yaw: ' + str(yaw))
Logger.print(f'Light: {blockP.getLight()}')



