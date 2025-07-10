from __future__ import annotations
import math


if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.logger import Logger, Style
    from libs.utils.dictionary import Dictionary
    from libs.walk import Walk, Block, PathNotFoundError
    from libs.actions import Action
    from libs.state import State, Waypoint
    from libs.inventory import Inv
    from libs.craft import Craft
    from libs.explorer import Explorer
    from libs.scripts import Script


class NotMineableBlockError(Exception):
    """Raised when the block is not mineable"""
    pass


class Miner:
    """A class to handle miner gathering"""
    mineBlocks = { # TODO: make this a json file
        'minecraft:coal': {
            'level': 1,
            'source': ['minecraft:coal_ore', 'minecraft:deepslate_coal_ore'],
            'minKeep': 32, # keep at least 32 coal, if more, just mine if its the objective
            'tool': 'pickaxe',
        },
        'minecraft:raw_iron': {
            'level': 2,
            'source': ['minecraft:iron_ore', 'minecraft:deepslate_iron_ore', 
                    'minecraft:raw_iron_block'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:raw_copper': {
            'level': 2,
            'source': ['minecraft:copper_ore', 'minecraft:deepslate_copper_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:raw_gold': {
            'level': 3,
            'source': ['minecraft:gold_ore', 'minecraft:deepslate_gold_ore', 
                    'minecraft:raw_gold_block'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:redstone': {
            'level': 3,
            'source': ['minecraft:redstone_ore', 'minecraft:deepslate_redstone_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:lapis_lazuli': {
            'level': 3,
            'source': ['minecraft:lapis_ore', 'minecraft:deepslate_lapis_ore'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:diamond': {
            'level': 3,
            'source': ['minecraft:diamond_ore', 'minecraft:deepslate_diamond_ore'],
            'minKeep': math.inf, # mine all diamonds
            'tool': 'pickaxe',
        },
        'minecraft:emerald_ore': {
            'level': 3,
            'source': ['minecraft:emerald_ore', 'minecraft:deepslate_emerald_ore'],
            'minKeep': math.inf, # mine all emeralds
            'tool': 'pickaxe',
        },
        'minecraft:obsidian': {
            'level': 4,
            'source': ['minecraft:obsidian'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:cobblestone': {
            'level': 1,
            'source': ['minecraft:stone'],
            'minKeep': 0, # not keep, will naturally get cobblestone
            'tool': 'pickaxe',
            'tags': ['minecraft:stone_tool_materials']
        },
        'minecraft:blackstone': {
            'level': 1,
            'source': ['minecraft:blackstone'],
            'minKeep': 0,
            'tool': 'pickaxe',
            'tags': ['minecraft:stone_tool_materials']
        },
        'minecraft:andesite': {
            'level': 1,
            'source': ['minecraft:andesite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:granite': {
            'level': 1,
            'source': ['minecraft:granite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:diorite': {
            'level': 1,
            'source': ['minecraft:diorite'],
            'minKeep': 0,
            'tool': 'pickaxe',
        },
        'minecraft:dirt': {
            'level': 1,
            'source': ['minecraft:dirt'],
            'minKeep': 0,
            'tool': 'shovel',
        },
    }

    @staticmethod
    def getSourceOres(ids: str | list[str] = None) -> list[str]:

        if isinstance(ids, str):
            ids = [ids]

        ores = []
        for i, block in Miner.mineBlocks.items():
            if ids is not None:
                ids_ = [i]
                if 'tags' in block:
                    ids_.extend(block['tags'])

                r = set(ids).intersection(set(ids_))
                if len(r) == 0:
                    continue
                
            ores.extend(block['source'])

        return ores
    

    @staticmethod
    def getMineableItems(ids: str | list[str] = None) -> list[str]:
        """Get the mineable items"""

        if isinstance(ids, str):
            ids = [ids]

        items = []
        for block in Miner.mineBlocks:
            items.append(block)
            if 'tags' in Miner.mineBlocks[block]:
                for tag in Miner.mineBlocks[block]['tags']:
                    items.append(tag)

        if ids is not None:
            ids = [i for i in ids if i in ids]
        
        return items


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

        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]

        if minePlace is None or Calc.distance(minePlace, pos) > 350:
            minePlace = Explorer.searchGoodPlaceToBuild(radius=32) # center of a 5x5 flat area
            if len(minePlace) == 0:
                raise Exception('No place found to start mining')
            
            minePlace = minePlace[0]
            Miner.setMinePlace(minePlace)

        region = Region.createRegion(minePlace, 2)
        Walk.walkTo(region)        


    @staticmethod
    def getBlockSource(id: str) -> str:
        """Get the block source"""
        if id in Miner.mineBlocks:
            return Miner.mineBlocks[id]['source'][0]
        return None
    
    @staticmethod
    def searchBlockOrItem(id: str) -> dict | None:
        """Search for a block or item"""
        if id in Miner.mineBlocks:
            return Miner.mineBlocks[id]
        
        for block in Miner.mineBlocks:
            if id in Miner.mineBlocks[block]['source']:
                return Miner.mineBlocks[block]
            if 'tags' in Miner.mineBlocks[block] and id in Miner.mineBlocks[block]['tags']:
                return Miner.mineBlocks[block]
        
        return None

    @staticmethod
    def assertPickaxeLevel(id: str) -> bool:
        """Check the pickaxe level for a block"""
        actualLevel = Inv.getEquippedToolLevel('pickaxe')
        block = Miner.searchBlockOrItem(id)
        Logger.debug(f'Checking pickaxe level for {id}...')
        if block == None:
            return True
        
        Logger.debug(f'Block {id} level: {block["level"]} | actual level: {actualLevel}')
        if actualLevel < block['level']:
            Craft.craft(id=Inv.getToolByLevel('pickaxe', block['level']))
            return False

        return True

    @staticmethod
    def getMinKeep() -> dict:
        minKeep = {}
        for key, item in Miner.mineBlocks.items():
            if 'minKeep' in item:
                minKeep[key] = item['minKeep']

        return minKeep
            

    @staticmethod
    def getOres(objective: dict = None, radius: int = 1) -> list:
        if objective is None:
            objective = {}
        else:
            objective = objective.copy()

        minKeep = Miner.getMinKeep()
        invCount = Inv.countItems()
        for key, item in minKeep.items():
            c = invCount.get(key, 0)
            if item <= c: continue
            objective[key] = objective.get(key, 0) + item

        if len(objective) == 0: return []

        ids = []
        for key in objective:
            ids.extend(Dictionary.getIds(key))

        ores = Miner.getSourceOres(ids)

        blocks = []
        for id_ in ores:
            blocks += World.findBlocksMatching(id_, radius)


        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]

        blocks = sorted(blocks, key=lambda b: Calc.distance(pos, [b.x, b.y, b.z]))

        return blocks


    @staticmethod
    def mineStepDown(objective: dict[str, int], step: int = 5):
        """Mine a step down"""
        step_ = step
        if step_ < 0:
            raise ValueError('Step must be greater than 0')

        Logger.info(f'Mining step down {step_} blocks')

        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]
        pos[1] -= step_ * 2
        if pos[1] < -63:
            pos[1] = -63

        region = Region.createRegion(pos, [step_*2, step_*2, step_*2])

        checker = lambda x: Miner.checkObjective(objective)

        # canBreakUnder=False to try create a stair
        Walk.walkTo(
            region,
            canBreakUnder=False, weightMask=0.1, timeLimit=2,
            earlyMoveReturnCallback=checker,
        )
    

    @staticmethod
    def mineStep(objective: dict[str, int], step: int = 5, layer: int = -60):
        """Mine a step"""
        if step < 0:
            raise ValueError('Step must be greater than 0')

        pos = Player.getPlayer().getPos()
        if pos.y > layer:
            Miner.mineStepDown(objective, step)
        
        else:
            # Miner.mineStepForward(step)
            raise NotImplementedError('Mine step forward not implemented yet')
        
        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]


    @staticmethod
    def mineOres(objective: dict[str, int], radius:int = 2):
        maxDistance = radius * 16

        listener = Script.scriptListener('mineOres')
        error = None
        try:
            while True:
                if Miner.checkObjective(objective):
                    break

                blocks = Miner.getOres(objective=objective, radius=radius)
                b = False
                for block in blocks:
                    listener()
                    if Miner.checkObjective(objective):
                        break

                    pos = Player.getPlayer().getPos()
                    pos = [pos.x, pos.y, pos.z]

                    if Calc.distance(pos, [block.x, block.y, block.z]) > maxDistance:
                        continue

                    block = Block.getBlock([block.x, block.y, block.z])

                    if not block.checkIfVisible():
                        continue

                    Logger.info(f'Mining {block.pos}')
                    try:
                        Action.breakBlock(block.pos)
                        Walk.collectDrops()
                    except Exception as e:
                        continue

                    b = True

                if b == False:
                    break
                
                Time.sleep(1000)
                Walk.collectDrops()

        except Exception as e:
            error = e

        finally:
            Script.stopScript('mineOres')

        if error is not None:
            raise error


    @staticmethod
    def mine(ids: str | dict[str, int]):
        """Mine a block"""
        if isinstance(ids, str):
            ids = {ids: 1}

        if not isinstance(ids, dict):
            raise
        
        Inv.sortHotbar()
        invItems = Inv.countItems()
        obj = {}
        for id, qtd in ids.items():
            id = Dictionary.getGroup(id)

            o = invItems.get(id, 0) + qtd
            block = Miner.searchBlockOrItem(id)

            if block == None:
                raise NotMineableBlockError(f'Block {id} is not mineable')

            obj[id] = obj.get(id, 0) + o
            
            Logger.info(f'Mining {id} x{qtd}')

            Miner.assertPickaxeLevel(id)

        listener = Script.scriptListener('miner')
        error = None
        try:
            Miner.goToMinePlace()
            while True:
                listener()

                if Miner.checkObjective(obj):
                    break

                Miner.mineStep(obj, 3)
                Miner.mineOres(obj)
                
                pos = Player.getPlayer().getPos()
                pos = [pos.x, pos.y, pos.z]
                Miner.setMinePlace(pos)

        except Exception as e:
            error = e

        finally:
            Script.stopScript('miner')
            

        if error != None:
            raise error


    @staticmethod
    def checkObjective(objective: dict) -> bool:
        invItems = Inv.countItems()
        Logger.debug(f'Checking objective {objective}...')
        for key, c in objective.items():
            cInv = invItems.get(key, 0)
            Logger.debug(f'{key} - {cInv}/{c}')
            if cInv < c: return False

        return True


Miner.mine = Craft.collectionMethod(Miner.getMineableItems())(Miner.mine)
