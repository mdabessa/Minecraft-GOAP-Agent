if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.scripts import Script
    from libs.walk import Walk
    from libs.actions import Action
    from libs.inventory import Inv
    from libs.craft import Craft


class NoTreeFound(Exception):
    """Raised when no tree is found."""
    pass


class Wood:
    """A class to handle wood gathering"""
    @staticmethod
    def isRoot(pos: list) -> bool:
        """Check if pos is a root of a tree"""
        floor = World.getBlock(int(pos[0]), int(pos[1]) - 1, int(pos[2]))
        if floor == None: return False
        return floor.getId() in ['minecraft:grass_block', 'minecraft:dirt']


    @staticmethod
    def searchTree(radius: int = 100) -> list:
        """Search for trees in a radius and return a list of positions of the roots"""

        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]
        
        blocks = []
        ids = Dictionary.getIds('minecraft:logs')
        for id in ids:
            blocks += World.findBlocksMatching(id, radius)

        blocks = [b for b in blocks if Wood.isRoot([b.x, b.y, b.z])]

        blocks = sorted(blocks, key=lambda b: Calc.distance(pos, [b.x, b.y, b.z]))
        
        return blocks


    @staticmethod
    def cutTree(pos: list):
        """Cut a tree at pos"""
        region = Region.createRegion(pos, [5, 7, 5])
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
                    Logger.debug('No trees found, exploring...')
                    raise NotImplementedError('Exploration not implemented yet') # TODO: explore function
                else:
                    raise NoTreeFound('No trees found in the area')

            for tree in trees:
                listener()
                pos = [tree.x, tree.y, tree.z]
                Logger.debug(f'Cutting tree at {pos}')
                region = Region.createRegion(pos, 5)
                Walk.walkTo(region, canPlace=False, allowListBreak=['minecraft:logs', 'minecraft:leaves'])
                Wood.cutTree(pos)
                Time.sleep(1000) # wait for the blocks to drop
                Walk.collectDrops()
                
                _count = Inv.countItems()
                _count = _count.get('minecraft:logs', 0)
                if _count >= count + quantity:
                    break

            if _count >= count + quantity:
                break

            else:
                raise NoTreeFound('No trees found in the area') # TODO: explore function
