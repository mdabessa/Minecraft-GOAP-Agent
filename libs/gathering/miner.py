import math


if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.walk import Walk
    from libs.actions import Action
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
            Action.placeBlock(pos, 'minecraft:torch', moveToPlace=False, fastPlace=True, faces=[0, 1, 0]) # place on the ground

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
        actualLevel = Inv.getToolLevel('pickaxe')
        level = Miner.searchBlockOrItem(id)
        if level == None: return False
        return actualLevel >= level['level']


