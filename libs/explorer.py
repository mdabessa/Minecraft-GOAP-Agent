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
    def _searchGoodPlaceToBuild(radius: int = 32, timeLimit: int = 2, listener: callable = lambda:None, **kwargs) -> list:
        """Search good places to build"""
        center = Player.getPlayer().getPos()
        center = [int(center.x), int(center.y), int(center.z)]

        shape = kwargs.get('shape', [radius, radius, radius])
        steps = kwargs.get('steps', [1, 1, 1])

        products = Explorer.iteratePos(center, shape, steps)
        places = []
        start = time.time()
        for pos in products:
            listener()
            if time.time() - start > timeLimit: break
            if Explorer.placeablePlace(pos): places.append(pos)

        return places
                
    
    @staticmethod
    def searchGoodPlaceToBuild(radius: int = 32, **kwargs) -> list:
        """Search good places to build"""

        listener = Script.scriptListener('searchGoodPlaceToBuild')
        error = None
        try:
            return Explorer._searchGoodPlaceToBuild(radius, listener=listener, **kwargs)
        except Exception as e:
            error = e
        finally:
            Script.stopScript('searchGoodPlaceToBuild')
            
        if error != None:
            raise error


    @staticmethod
    def placeablePlace(pos: int) -> bool:
        """Check if pos is a place that can be built"""

        if Block.getBlock(pos).isSolid: return False
        
        # check if there is a solid block around pos
        for x, y, z in itertools.product([-1, 0, 1], repeat=3):
            if x == y == z == 0: continue
            if Block.getBlock([pos[0]+x, pos[1]+y, pos[2]+z]).isSolid:
                return True

        return False
        
        
    @staticmethod
    def getFloor(pos: list) -> list:
        """Get the floor of pos"""
        min_ = -64
        max_ = 320
        
        for y in range(max_, min_, -1):
            block = Block.getBlock([pos[0], y, pos[2]])
            if block is None: continue

            if block.isSolid or block.isLiquid:
                return [pos[0], y, pos[2]]
        
        return [pos[0], min_, pos[2]]

         