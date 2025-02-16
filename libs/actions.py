import time
import math

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.logger import Logger
    from libs.scripts import Script
    from libs.inventory import Inv, NotEnoughItemsError
    from libs.walk import Walk, Block, PathNotFoundError


class OutOfReachError(Exception):
    """Raised when the player is out of reach."""
    pass


class BlockNotVisibleError(Exception):
    """Raised when the block is not visible."""
    pass


class PositionNotValidError(Exception):
    """Raised when the position is not valid."""
    pass


class FailedToBreakError(Exception):
    """Raised when the block failed to break."""
    pass

class FailedToPlaceError(Exception):
    """Raised when the block failed to place."""
    pass


class Action:
    """A class to handle actions"""
    @staticmethod
    def waitStop():
        while True:
            vel = Player.getPlayer().getVelocity()
            vel = [vel.x, vel.y, vel.z]
            check = False
            for v in vel:
                if v > 0.1:
                    check = True
            
            time.sleep(0.1)
            
            if not check:
                break


    @staticmethod
    def jump():
        """Jump"""
        KeyBind.pressKey("key.keyboard.space")
        Client.waitTick(1)
        KeyBind.releaseKey("key.keyboard.space")
    

    @staticmethod
    def breakBlock(pos: list[int] | list[list[int]], safe: bool = True, sortTools: bool = True):
        """Break a block at pos"""
        if not isinstance(pos[0], list):
            pos = [pos]

        # sort the pos by distance to the player
        playerPos = Player.getPlayer().getPos()
        playerPos = [playerPos.x, playerPos.y, playerPos.z]
        pos = sorted(pos, key=lambda p: Calc.distance(p, playerPos))

        listener = Script.scriptListener('breakBlock')
        error = None
        try:
            for p in pos:
                p = [math.floor(p[0]), math.floor(p[1]), math.floor(p[2])]
                if sortTools:
                    betterTool = Inv.getBetterTool(p)
                    if betterTool != None:
                        Inv.selectTool(betterTool['tool'])
                        Client.waitTick(1)
                    else:
                        Inv.selectNonTool()
                        Client.waitTick(1)

                player = Player.getPlayer()
                block = Block.getBlock(p)
                if not block.isSolid: continue
                
                if safe:
                    point = block.getInteractPoint(resolution=2)
                    if point == None:
                        # TODO: add the block to a check list, continue, and
                        # check the block again after breaking another block
                        # if the block is still not visible, then raise an error
                        raise BlockNotVisibleError(f'Block at {p} is not visible')
                else:
                    point = [block.pos[0] + 0.5, block.pos[1] + 0.5, block.pos[2] + 0.5]

                while True:
                    listener()
                    player.lookAt(point[0], point[1], point[2])
                
                    _block = Block.getBlock(p)
                    if _block.id != block.id:
                        break

                    KeyBind.pressKey('key.mouse.left')
                    Client.waitTick(1)
                
                KeyBind.releaseKey('key.mouse.left')

        except Exception as e:
            error = e
        
        finally:
            KeyBind.releaseKey('key.mouse.left')
            Script.stopScript('breakBlock')

        if error is not None:
            raise error


    @staticmethod
    def breakAllBlocks(blockId: str, region: Region, safe: bool = True):
        """Break all blocks of blockId in region"""
        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]
        reach = Player.getReach()

        blocks = World.findBlocksMatching(blockId, 1)

        blocks = [b for b in blocks if region.contains([b.x, b.y, b.z]) 
                and Calc.distance(pos, [b.x, b.y, b.z]) <= reach]

        blocks = sorted(blocks, key=lambda b: Calc.distance(pos, [b.x, b.y, b.z]))
        Inv.sortHotbar()
        listener = Script.scriptListener('breakAllBlocks')
        error = None
        try:
            for block in blocks:
                listener()
                block_ = Block.getBlock([math.floor(block.x), math.floor(block.y), math.floor(block.z)])
                if not block_.isSolid: continue
                if block_.id != blockId: continue
        
                Action.breakBlock([block.x, block.y, block.z], safe=safe)
                Client.waitTick(1)

        except Exception as e:
            error = e

        finally:
            Script.stopScript('breakAllBlocks')

        if error is not None:
            raise error

    @staticmethod
    def placeBlock(pos: list, blockId: str | list[str], moveToPlace: bool = True):
        """Place a block at pos"""
    
        if isinstance(blockId, str):
            blockId = [blockId]
        
        items = Inv.countItems()
        item = None
        for id in blockId:
            if id in items and items[id] > 0:
                item = id
                break

        if item == None:
            raise NotEnoughItemsError(f'Not enough items to place {blockId}')
        
        if moveToPlace:
            # Ensure that the player is not in the region to place the block
            region = Region.createRegion(pos, 1)        
            Walk.walkTo(region, reverse=True, timeLimit=1)

        Inv.selectBuildingBlock(item)
        player = Player.getPlayer()

        block = Block.getBlock(pos)
        if block.isSolid:
            raise PositionNotValidError(f'Position {pos} is not a valid position to place {blockId}')
        
        point = block.getInteractPoint(opposite=True, solid=True)
        if point == None:
            raise BlockNotVisibleError(f'Block at {pos} does not have visible support faces to place {blockId}')

        reach = Player.getReach()
        playerPos = Player.getPlayer().getPos()
        playerPos = [playerPos.x, playerPos.y, playerPos.z]
        if Calc.distance(playerPos, point) > reach:
            raise OutOfReachError(f'Player is out of reach to place {blockId} at {pos}')

        start = time.time()
        while True:
            playerPos = Player.getPlayer().getPos()
            playerPos = [playerPos.x, playerPos.y, playerPos.z]
            if Calc.distance(playerPos, point) < 1:
                # jump if the player is too close to the block,
                # this can make the player place blocks under them
                Action.jump()

            player.lookAt(point[0], point[1], point[2])
            KeyBind.pressKey('key.mouse.right')
            Client.waitTick(1)
            KeyBind.releaseKey('key.mouse.right')
            Client.waitTick(1)

            _block = Block.getBlock(pos)
            if _block.isSolid:
                break

            if time.time() - start > 2:
                raise FailedToPlaceError(f'Failed to place {blockId} at {pos}')


    @staticmethod
    def interactBlock(pos: list):
        """Interact with a block at pos"""
        Logger.debug(f'Interacting with block at {pos}')
        player = Player.getPlayer()
        player.lookAt(math.floor(pos[0]) + 0.5, math.floor(pos[1]) + 0.5, math.floor(pos[2]) + 0.5)

        reach = Player.getReach()
        
        block = Action.rayTraceBlock()
        if ((block is None) or (Calc.distance([
            math.floor(block.getX()), math.floor(block.getY()), math.floor(block.getZ())], pos) != 0)): 

            block = Block.getBlock(pos)
            point = block.getInteractPoint()
            if point == None:
                raise BlockNotVisibleError(f'Block at {pos} is not visible')

            playerPos = Player.getPlayer().getPos()
            playerPos = [playerPos.x, playerPos.y, playerPos.z]
            if Calc.distance(playerPos, point) > reach:
                raise OutOfReachError(f'Player is out of reach to interact with block at {pos}')

            player.lookAt(point[0], point[1], point[2])

        Client.waitTick(1)
        KeyBind.pressKey('key.mouse.right')
        Client.waitTick(1)
        KeyBind.releaseKey('key.mouse.right')


    @staticmethod
    def rayTraceBlock(steps: float = 0.1, maxDistance: float = None):
        """Ray trace and return the first block"""
        if maxDistance is None:
            maxDistance = Player.getReach()

        for i in range(1, int(maxDistance / steps)):
            reach = i * steps

            block = Player.rayTraceBlock(reach, False)
            if block is not None and block.getId() != 'minecraft:air':
                return block
            
        return None
        