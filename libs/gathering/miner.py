import math


if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.utils.logger import Logger
    from libs.scripts import Script
    from libs.walk import Walk, Block
    from libs.actions import Action, NotEnoughItemsError
    from libs.state import State, Waypoint
    from libs.inventory import Inv
    from libs.craft import Craft
    from libs.explorer import Explorer


class Miner:
    """A class to handle miner gathering"""
    mineBlocks = { # TODO: make this a json file
        'minecraft:coal': {
            'level': 1,
            'ore': ['minecraft:coal_ore', 'minecraft:deepslate_coal_ore'],
            'minKeep': 32, # keep at least 32 coal, if more, just mine if its the objective
            'tool': 'pickaxe',
        },
        'minecraft:raw_iron': {
            'level': 2,
            'ore': ['minecraft:iron_ore', 'minecraft:deepslate_iron_ore', 
                    'minecraft:raw_iron_block'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:raw_copper': {
            'level': 2,
            'ore': ['minecraft:copper_ore', 'minecraft:deepslate_copper_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:raw_gold': {
            'level': 3,
            'ore': ['minecraft:gold_ore', 'minecraft:deepslate_gold_ore', 
                    'minecraft:raw_gold_block'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:redstone': {
            'level': 3,
            'ore': ['minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:lapis_lazuli': {
            'level': 3,
            'ore': ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:diamond': {
            'level': 3,
            'ore': ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore'],
            'minKeep': math.inf, # mine all diamonds
            'tool': 'pickaxe',
        },
        'minecraft:emerald_ore': {
            'level': 3,
            'ore': ['minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore'],
            'minKeep': math.inf, # mine all emeralds
            'tool': 'pickaxe',
        },
        'minecraft:obsidian': {
            'level': 4,
            'ore': ['minecraft:obsidian'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:cobblestone': {
            'level': 1,
            'ore': ['minecraft:stone'],
            'minKeep': 0, # not keep, will naturally get cobblestone
            'tool': 'pickaxe',
        },
        'minecraft:andesite': {
            'level': 1,
            'ore': ['minecraft:andesite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:granite': {
            'level': 1,
            'ore': ['minecraft:granite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:diorite': {
            'level': 1,
            'ore': ['minecraft:diorite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:dirt': {
            'level': 1,
            'ore': ['minecraft:dirt'],
            'minKeep': 0,
            'tool': 'shovel',
        },
    }

    @staticmethod
    def getMinePlace() -> list:
        """Get the mine place"""
        wp = Waypoint.getWaypoint('.minePlace') 
        if wp is not None:
            return [wp.x, wp.y, wp.z]

        return None
    
    @staticmethod
    def setMinePlace(pos: list):
        """Set the mine place"""
        dimention = World.getDimension()
        Waypoint.addWaypoint('.minePlace', *pos, dimention)

    @staticmethod
    def goToMinePlace():
        """Go to the mine place"""
        minePlace = Miner.getMinePlace()
        if minePlace == None:
            minePlace = Explorer.searchGoodPlaceToBuild(radius=32) # center of a 5x5 flat area
            if len(minePlace) == 0:
                raise Exception('No place found to start mining')
            
            minePlace = minePlace[0]
            Miner.setMinePlace(minePlace)

        region = Region.createRegion(minePlace, 2)
        Walk.walkTo(region)        


    @staticmethod
    def placeTorch():
        """Place a torch"""
        player = Player.getPlayer()
        pos = player.getPos()
        yaw = player.getYaw()
        pitch = player.getPitch()

        pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
        light = World.getBlockLight(*pos)
        
        if light > 2: return

        try:
            Action.placeBlock(pos, 'minecraft:torch', moveToPlace=False, faces=[0, 1, 0]) # place on the ground

            player.lookAt(yaw, pitch)
        except NotEnoughItemsError:
            pass


    @staticmethod
    def getBlockSource(id: str) -> str:
        """Get the block source"""
        if id in Miner.mineBlocks:
            return Miner.mineBlocks[id]['ore'][0]
        return None
    
    @staticmethod
    def searchBlockOrItem(id: str) -> dict | None:
        """Search for a block or item"""
        if id in Miner.mineBlocks:
            return Miner.mineBlocks[id]
        
        for block in Miner.mineBlocks:
            if id in Miner.mineBlocks[block]['ore']:
                return Miner.mineBlocks[block]
        
        return None

    @staticmethod
    def checkPickaxeLevel(id: str) -> bool:
        """Check the pickaxe level for a block"""
        actualLevel = Inv.getActualToolLevel('pickaxe')
        level = Miner.searchBlockOrItem(id)
        if level == None: return False
        return actualLevel >= level['level']


    @staticmethod
    def mine():
        # TODO: Temporary mine gathering
        stopBlocks = ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore',
                    'minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore'
                    'minecraft:iron_ore', 'minecraft:deepslate_iron_ore',
                    'minecraft:gold_ore', 'minecraft:deepslate_gold_ore',
                      ]
        
        block = Block.getLookAtBlock()
        pos = Player.getPlayer().getPos()
        pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
        direction = block.pos[0] - pos[0], block.pos[2] - pos[2]
        if direction[0] == 0 and direction[1] == 0:
            direction = 0, 1
        
        listener = Script.scriptListener('simpleMine')
        while True:
            KeyBind.releaseKey('key.keyboard.w')
            Miner.placeTorch()
            listener()
            KeyBind.pressKey('key.keyboard.w')

            if not Miner.checkPickaxeLevel('minecraft:diamond_ore'):
                raise Exception('Pickaxe level is not enough')
            
            dur = Inv.getToolDurability('pickaxe')
            if dur < 50:
                raise Exception('Pickaxe is about to break')

            block = Block.getLookAtBlock()
            if block is not None:
                pos = Player.getPlayer().getPos()
                pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
                
                while True: # Gravel/sand
                    listener()
                    nextPos1 = [pos[0] + direction[0], pos[1]+1, pos[2] + direction[1]]
                    nextPos2 = [pos[0] + direction[0], pos[1]+2, pos[2] + direction[1]]
                    block1 = Block.getBlock(nextPos1)
                    block2 = Block.getBlock(nextPos2)

                    Action.breakBlock(nextPos1, safe=False)            
                    
                    if block1.id in ['minecraft:gravel', 'minecraft:sand'] or \
                        block2.id in ['minecraft:gravel', 'minecraft:sand']:
                        
                        Client.waitTick(20)
                        KeyBind.releaseKey('key.keyboard.w')

                    
                    block1 = Block.getBlock(nextPos1)

                    if block1 is not None and block1.isLiquid:
                        KeyBind.releaseKey('key.keyboard.w')
                        KeyBind.pressKey('key.keyboard.s') # go back
                        raise Exception('Liquid found')

                    if block1 is None or not block1.isSolid:
                        break
                
                KeyBind.pressKey('key.keyboard.w')
                nextPos1 = [pos[0] + direction[0], pos[1], pos[2] + direction[1]]
                Action.breakBlock(nextPos1, safe=True)

                nextPos3 = [pos[0] + direction[0], pos[1]-1, pos[2] + direction[1]]
                block = Block.getBlock(nextPos3)
                if block is None or not block.isSolid:
                    KeyBind.releaseKey('key.keyboard.w')
                    raise Exception('Block is not solid')

                for x in (-1, 1):
                    for y in (0, 1):
                        for z in (-1, 1):
                            blocksPos = [pos[0] + x, pos[1] + y, pos[2] + z]
                            block = Block.getBlock(blocksPos)
                            if block is not None and block.id in stopBlocks:
                                KeyBind.releaseKey('key.keyboard.w')
                                Logger.print(f'Goal block found: {block.id}')
                                return
                
                blockPos = [pos[0], pos[1]-1, pos[2]]
                block = Block.getBlock(blockPos)
                if block is None or block.id in stopBlocks:
                    KeyBind.releaseKey('key.keyboard.w')
                    Logger.print(f'Goal block found: {block.id}')
                    return
                
                blockPos = [pos[0], pos[1]+2, pos[2]]
                block = Block.getBlock(blockPos)
                if block is not None and block.id in stopBlocks:
                    KeyBind.releaseKey('key.keyboard.w')
                    Logger.print(f'Goal block found: {block.id}')
                    return


