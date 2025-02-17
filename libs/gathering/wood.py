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

        Action.breakAllBlocks(block.getId(), region, safe=False)


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
            
            _count = Inv.countItems()
            _count = _count.get('minecraft:logs', 0)

            if _count >= count + quantity:
                break
