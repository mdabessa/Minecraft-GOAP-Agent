if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
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
        region = Region.createRegion(pos, [3, 7, 3])
        block = World.getBlock(int(pos[0]), int(pos[1]), int(pos[2]))
        if block == None: return

        Action.breakAllBlocks(block.getId(), region, safe=False)


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
                Action.placeBlock(pos, 'minecraft:saplings', faces=[0, 1, 0])
            except Exception as e:
                Logger.warning(f'Error planting sapling: {e}')
                return

    @staticmethod
    @Craft.collectionMethod(Dictionary.getIds('minecraft:logs'))
    def gatherWood(objective: dict = None, exploreIfNoWood: bool = True):
        """Gather wood"""
        if objective is None:
            quantity = 1

        else:
            quantity = 0
            for key, item in objective.items():
                quantity += item


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
            pos = [tree.x, tree.y, tree.z]
            Logger.debug(f'Cutting tree at {pos}')
            region = Region.createRegion(pos, 5)
            Walk.walkTo(region)
            Wood.cutTree(pos)
            Time.sleep(3000) # wait for the blocks to drop
            Walk.collectDrops()
            
            _count = Inv.countItems()
            _count = _count.get('minecraft:logs', 0)
            if _count >= count + quantity:
                break
        else:
            raise NoTreeFound('No trees found in the area') # TODO: explore function

    