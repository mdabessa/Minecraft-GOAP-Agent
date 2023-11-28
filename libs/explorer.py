import itertools
import time

if __name__ == "":
    from JsMacrosAC import *
    from libs.walk import Walk, Block
    from libs.scripts import Script



class Explorer:
    @staticmethod
    def iteratePos(center: list, shape: list, steps: list):
        """Iterate over pos in a shape from center. Yield pos"""
        assert len(center) == len(shape) == len(steps), 'center, shape and steps must have the same length'
        
        max_ = max(shape)
        
        # layers, generate empty cubes from inside to outside
        for i in range(1, max_+1):
            ranges = [range(-i, i+1)] * len(shape)
            # loop for each axis
            for axis in range(len(shape)):
                ranges[axis] = (-i, i)
                # loop pos
                for pos in itertools.product(*ranges):
                    if all([pos[index]%steps[index] == 0 for index in range(len(pos))]):
                        yield [center[index] + pos[index] for index in range(len(pos))]
                    
                ranges[axis] = range(-i+1, i) # avoid double pos


    @staticmethod
    def _searchGoodPlaceToBuild(radius: int = 32, timeLimit: int = 2, range_: int = 1, listener: callable = lambda:None, **kwargs) -> list:
        """Search good places to build"""
        center = Player.getPlayer().getPos()
        center = [int(center.x), int(center.y), int(center.z)]

        shape = kwargs.get('shape', [radius, radius, radius])
        steps = kwargs.get('steps', [1, 5, 1])

        products = Explorer.iteratePos(center, shape, steps)
        places = []
        start = time.time()
        for pos in products:
            listener()
            if time.time() - start > timeLimit: break
            if Explorer.goodPlaceToBuild(pos, range_): places.append(pos)

        return places
                
    
    @staticmethod
    def searchGoodPlaceToBuild(radius: int = 32, range_: int = 1, **kwargs) -> list:
        """Search good places to build"""

        listener = Script.scriptListener('searchGoodPlaceToBuild')
        error = None
        try:
            return Explorer._searchGoodPlaceToBuild(radius, listener=listener, range_ = range_, **kwargs)
        except Exception as e:
            error = e
        finally:
            Script.stopScript('searchGoodPlaceToBuild')
            
        if error != None:
            raise error


    @staticmethod
    def goodPlaceToBuild(pos: int, range_: int = 1) -> bool:
        """Check if pos is a good place to build"""
        
        # 3x3 with max of 1 block of height difference
        min_ = -range_
        max_ = range_ + 1
        walk = Walk(pos, pos)
        positions = []
        for x, z in itertools.product(range(min_, max_), range(min_, max_)):
            pos_ = walk.getWalkablePos([pos[0]+x, pos[1], pos[2]+z], pos)
            if pos_ == None: return False
            positions.append(pos_)

        max__ = max(positions, key=lambda p: p[1])[1]
        min__ = min(positions, key=lambda p: p[1])[1]

        if max__ - min__ > 1: return False

        return True


    @staticmethod
    def getFloor(pos: list) -> list:
        """Get the floor of pos"""
        min_ = -64
        max_ = 320
        
        for y in range(max_, min_, -1):
            block = Block.getBlock([pos[0], y, pos[2]])
            if block == None: continue

            if block.isSolid or block.isLiquid:
                return [pos[0], y, pos[2]]
        
        return [pos[0], min_, pos[2]]

         