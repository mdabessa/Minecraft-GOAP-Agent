import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.scripts import Script
    from libs.walk import Walk, Block
    from libs.actions import Action
    from libs.inventory import Inv
    from libs.craft import Craft


class NoTreeFound(Exception):
    """Raised when no tree is found."""
    pass


class Wood:
    """A class to handle wood gathering"""
    @staticmethod
    def treeRoot(pos: list, maxHeight: int = 5) -> list:
        """Check if pos is a tree and return the root position"""
        floor = Block.getBlock([math.floor(pos[0]), math.floor(pos[1]) - 1, math.floor(pos[2])])
        if floor == None: return []

        if floor.id in ['minecraft:grass_block', 'minecraft:dirt']:
            return pos

        top = Block.getBlock([math.floor(pos[0]), math.floor(pos[1]) + 1, math.floor(pos[2])])
        if top == None: return []

        if floor.isAir and Dictionary.getGroup(top.id) in ['minecraft:logs', 'minecraft:leaves']:
            for i in range(1, maxHeight + 1):
                floor_ = [math.floor(pos[0]), math.floor(pos[1]) - i, math.floor(pos[2])]
                block = Block.getBlock(floor_)
                if block == None: return []
                if block.isAir: continue
                if block.id in ['minecraft:grass_block', 'minecraft:dirt']:
                    return [floor_[0], floor_[1] + 1, floor_[2]]
                
                break
    
        return []

    @staticmethod
    def searchTree(radius: int = 100, maxTrees: int = 1) -> list:
        """Search for trees in a radius and return a list of positions of the roots"""

        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]
        
        blocks = []
        ids = Dictionary.getIds('minecraft:logs')
        for id in ids:
            blocks += World.findBlocksMatching(id, radius)

        trees = []
        for block in blocks:
            tree = Wood.treeRoot([block.x, block.y, block.z])
            if tree:
                trees.append(tree)

        trees = sorted(trees, key=lambda b: Calc.distance(pos, b))#[b.x, b.y, b.z]))
        
        if maxTrees > 0:
            trees = trees[:maxTrees]

        return trees


    @staticmethod
    def cutTree(pos: list):
        """Cut a tree at pos"""
        region = Region.createRegion(pos, [5, 9, 5])
        block = World.getBlock(int(pos[0]), int(pos[1]), int(pos[2]))
        if block == None: return

        Action.breakAllBlocks('minecraft:logs', region, safe=False)


    @staticmethod
    def plantSapling(distance: int = 5, minTreeDistance: int = 1):
        """Plant a sapling if possible"""
        Logger.print('Planting sapling')
        saplings = Inv.countItem('minecraft:saplings')
        if saplings == 0:
            Logger.warning('No saplings in inventory')
            return

        dirts = []
        for id in Dictionary.getIds('minecraft:dirt'):
            dirts += World.findBlocksMatching(id, 1)

        saplings_block = []
        for id in Dictionary.getIds('minecraft:saplings'):
            saplings_block += World.findBlocksMatching(id, 1)
        
        logs = []
        for id in Dictionary.getIds('minecraft:logs'):
            logs += World.findBlocksMatching(id, 1)

        playerPos = Player.getPlayer().getPos()
        playerPos = [playerPos.x, playerPos.y, playerPos.z]

        places = []
        for dirt in dirts:
            pos = [math.floor(dirt.x), math.floor(dirt.y) + 1, math.floor(dirt.z)]
            top = Block.getBlock(pos)
            if top == None or not top.isAir: continue

            if any(Calc.distance(pos, [log.x, log.y, log.z]) < minTreeDistance for log in logs): continue
            if any(Calc.distance(pos, [sapling.x, sapling.y, sapling.z]) < minTreeDistance for sapling in saplings_block): continue

            if Calc.distance(playerPos, pos) > distance: continue
            places.append(pos)

  
        places = sorted(places, key=lambda b: Calc.distance(playerPos, b))

        if len(places) == 0:
            Logger.warning('No place to plant sapling')
            return

        for pos in places:
            try:
                Logger.debug(f'Planting sapling at {places[0]}')
                Action.placeBlock(pos, 'minecraft:saplings', fastPlace=False, faces=[0, 1, 0])
            except Exception as e:
                Logger.warning(f'Error planting sapling: {e}')
                return

    @staticmethod
    @Craft.collectionMethod(Dictionary.getIds('minecraft:logs'))
    def gatherWood(quantity: int = 1, exploreIfNoWood: bool = True):
        """Gather wood
        :param quantity: the amount of wood to gather
        :param exploreIfNoWood: if True, explore if no wood is found
        """
        if quantity <= 0:
            raise ValueError('quantity must be greater than 0')
        
        listener = Script.scriptListener('gatherWood')
        while True:
            listener()
            count = Inv.countItems()
            count = count.get('minecraft:logs', 0)
            trees = Wood.searchTree()
            if len(trees) == 0:
                if exploreIfNoWood:
                    Logger.info('No trees found, exploring...')
                    raise NotImplementedError('Exploration not implemented yet') # TODO: explore function
                else:
                    raise NoTreeFound('No trees found in the area')

            pos = trees[0]

            Logger.debug(f'Cutting tree at {pos}')
            region = Region.createRegion(pos, 3)

            try:
                Walk.walkTo(region, canPlace=False, allowListBreak=['minecraft:logs', 'minecraft:leaves'])
            except Exception as e:
                Logger.warning(f'Error walking to {pos}: {e}')
                continue
            
            Wood.cutTree(pos)

            Walk.collectDrops(walkPathKwargs={'canPlace': False, 'allowListBreak': ['minecraft:logs', 'minecraft:leaves']})
            
            Wood.plantSapling()

            _count = Inv.countItems()
            _count = _count.get('minecraft:logs', 0)

            if _count >= count + quantity:
                break
