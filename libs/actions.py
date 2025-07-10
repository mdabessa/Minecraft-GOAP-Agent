import time
import math
import itertools

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.logger import Logger
    from libs.utils.dictionary import Dictionary
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
    def break_(listener: callable = None):
        """Break looking at block"""
        player = Player.getPlayer()

        blockLook = Block.getLookAtBlock()
        if blockLook is None or blockLook.isAir:
            return
        
        if blockLook.isLiquid:
            raise PositionNotValidError('Cannot break liquid')

        block_ = Player.detailedRayTraceBlock(4.5, True)
        pos = block_.asBlock().getPos()

        Inv.sortHotbar()
        betterTool = Inv.getBetterTool(blockLook.pos)
        if betterTool != None:
            Inv.selectTool(betterTool['tool'], )
            Client.waitTick(1)
        else:
            Inv.selectNonTool()
            Client.waitTick(1)

        while True:
            if listener is not None:
                try:
                    listener()
                except Exception as e:
                    KeyBind.releaseKey('key.mouse.left')
                    raise e
            
            player.lookAt(pos.x, pos.y, pos.z)
            KeyBind.pressKey('key.mouse.left')
            Client.waitTick(1)

            block = Block.getBlock(blockLook.pos)
            if block.id != blockLook.id:
                break

        KeyBind.releaseKey('key.mouse.left')


    @staticmethod
    def breakBlock(pos: list[int] | list[list[int]], safe: bool = True):
    def breakBlock(pos: list[int] | list[list[int]], safe: bool = True, moveToBreak: bool = True, timeout: int = 10):
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
                
                player = Player.getPlayer()
                block = Block.getBlock(p)
                if not block.isSolid: continue
                
                playerPos = player.getPos()
                playerPos = [playerPos.x, playerPos.y, playerPos.z]
                reach = Player.getReach()
                point = block.getInteractPoint(resolution=2)
                if point is None:
                    if safe:
                        raise BlockNotVisibleError(f'Block at {p} is not visible')
                    else:
                        point = block.pos

                if Calc.distance(playerPos, point) > reach:
                    if moveToBreak:
                        region = Region.createRegion(block.pos, int(reach))
                        try:
                            Walk.walkTo(region, timeLimit=0.1)
                        except PathNotFoundError:
                            raise OutOfReachError()
                    else:
                        raise OutOfReachError()

                if moveToBreak:
                    region = Region.createRegion(block.pos, [1, 2, 1])        
                    Walk.walkTo(region, reverse=True, timeLimit=0.1, canPlace=False)

                if safe:
                    point = block.getInteractPoint(resolution=5)
                    if point == None:
                        # TODO: add the block to a check list, continue, and
                        # check the block again after breaking another block
                        # if the block is still not visible, then raise an error
                        raise BlockNotVisibleError(f'Block at {p} is not visible')
                else:
                    point = [block.pos[0] + 0.5, block.pos[1] + 0.5, block.pos[2] + 0.5]

                betterTool = Inv.getBetterTool(p)
                if betterTool != None:
                    Inv.selectTool(betterTool['tool'])
                else:
                    Inv.selectNonTool()
                    Client.waitTick(1)

                start = time.time()
                while True:
                    listener()
                    player.lookAt(point[0], point[1], point[2])
                
                    _block = Block.getBlock(p)
                    if _block.id != block.id:
                        break

                    KeyBind.pressKey('key.mouse.left')
                    Client.waitTick(1)
                    if time.time() - start > timeout:
                        raise TimeoutError()
                
                KeyBind.releaseKey('key.mouse.left')

        except Exception as e:
            error = e
        
        finally:
            KeyBind.releaseKey('key.mouse.left')
            Script.stopScript('breakBlock')

        if error is not None:
            raise error


    @staticmethod
    def breakAllBlocks(blockId: str = None, region: Region = None, safe: bool = True):
        """Break all blocks of blockId in region"""
        if blockId is None and region is None:
            raise ValueError('blockId or region must be provided')
        
        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]
        reach = Player.getReach()

        blocks = World.findBlocksMatching(blockId, 1)

        blocks = [b for b in blocks if region.contains([b.x, b.y, b.z]) 
                and Calc.distance(pos, [b.x, b.y, b.z]) <= reach]

        blocks = sorted(blocks, key=lambda b: Calc.distance(pos, [b.x, b.y, b.z]))
        
        listener = Script.scriptListener('breakAllBlocks')
        
        blocks = []
        for pos in region.iterate():
            listener()
            block = Block.getBlock(pos)
            if len(ids) > 0 and block.id not in ids:
                continue
            
            if block.isAir or block.isLiquid:
                continue

            blocks.append(pos)

        error = None
        try:
            listener()
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
    def placeBlock(pos: list, blockId: str | list[str], 
                   moveToPlace: bool = True, 
                   faces: list = None, exactId: bool = True):
        """Place a block at pos"""
    
        if isinstance(blockId, str):
            blockId = [blockId]
        
        blockId = [Dictionary.getGroup(i) for i in blockId]

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
        if not block.isLiquid and not block.isAir:
            raise PositionNotValidError(f'Position {pos} is not a valid position to place {blockId}')
        
        point = block.getInteractPoint(opposite=True, solid=True, faces=faces, resolution=5)
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
            if exactId and _block.id in blockId_:
                break
            elif not exactId and _block.isSolid:
            id_ = Dictionary.getGroup(_block.id)
            # Logger.print(f'{id_} in? {blockId}')

            if time.time() - start > 2:
                raise FailedToPlaceError(f'Failed to place {blockId} at {pos}')


    @staticmethod
    def interactBlock(pos: list):
        """Interact with a block at pos"""
        Logger.debug(f'Interacting with block at {pos}')
        player = Player.getPlayer()

        block = Block.getBlock(pos)
        point = block.getInteractPoint()
        if point == None:
            raise BlockNotVisibleError(f'Block at {pos} is not visible')

        playerPos = player.getPos()
        playerPos = [playerPos.x, playerPos.y, playerPos.z]
        if Calc.distance(playerPos, point) > Player.getReach():
            raise OutOfReachError(f'Player is out of reach to interact with block at {pos}')

        player.lookAt(point[0], point[1], point[2])

        Client.waitTick(1)
        KeyBind.pressKey('key.mouse.right')
        Client.waitTick(1)
        KeyBind.releaseKey('key.mouse.right')
