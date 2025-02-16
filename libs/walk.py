from __future__ import annotations
import time
import math
import itertools
import json
import threading


if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.scripts import Script
    from libs.actions import Action
    from libs.inventory import Inv


def encodePos(pos: list[int]) -> str:
    """Hash a position"""
    return f'{pos[0]}:{pos[1]}:{pos[2]}'


def decodePos(code: str) -> list[int]:
    """Unhash a position"""
    return [int(i) for i in code.split(':')]

class PathNotFoundError(Exception):
    """Exception raised when the path is not found"""
    pass


class Block:
    """A block in the world"""
    def __init__(self, state, pos: list[int]):
        self.id: str = state.getId()
        self.pos: list[int] = pos

        self.isAir: bool = state.isAir()
        self.isOpaque: bool = state.isOpaque()
        self.isLiquid: bool = state.isLiquid()
        self.isSolid: bool = state.isSolid()

        self.isWater: bool = self.id == "minecraft:water"
        self.isLava: bool = self.id == "minecraft:lava"


    def getFaces(self, fromPos: list = None, faces: list = None) -> list[dict]:
        """Get the block faces of a block and if the face is facing the fromPos"""
        if fromPos is None:
            fromPos = Player.getPlayer().getPos()
            # player eye pos
            fromPos = [fromPos.x, fromPos.y+1.62, fromPos.z] # TODO: get the correct player eye pos 

        if faces is None:
            faces = [1, 1, 1]

        faces_ = []
        for i in range(3):
            if faces[i] == 0: continue
            for j in range(-1, 2, 2):
                pos = self.pos[:]
                pos[i] += j
                neighbor = Block.getBlock(pos)
                
                pos = [self.pos[0]+0.5, self.pos[1]+0.5, self.pos[2]+0.5] # center of the block
                pos[i] += j * 0.499 # face position

                delta = fromPos[i] - pos[i]
                facing = False
                if delta > 0 and j == 1: facing = True
                if delta < 0 and j == -1: facing = True

                face = {
                    'pos': pos,
                    'facing': facing,
                    'neighbor': neighbor,
                    'face': i,
                }
    
                faces_.append(face)

        return faces_
    

    def getVisiblePoints(self, fromPos:list = None, resolution: int = 3, 
                         transparent: bool = False, solid: bool = False, opposite: bool = False,
                         earlyReturn: bool = False, faces: list = None) -> list[list[list[float]]]:
        """Get visible points of a block"""
        if transparent:
            # TODO: implement transparent visibility
            raise NotImplementedError('Transparent visibility is not implemented yet')
        
        if faces is None:
            faces = [1, 1, 1]

        if fromPos is None:
            fromPos = Player.getPlayer().getPos()
            # player eye pos
            fromPos = [fromPos.x, fromPos.y+1.62, fromPos.z]

        faces = self.getFaces(fromPos, faces)
        faces = [face for face in faces if face['facing'] != opposite]

        points = []
        for face in faces:
            if solid and not face['neighbor'].isSolid: continue

            for i, j in itertools.product(range(resolution), range(resolution)):
                point = face['pos'][:]
                index = [0, 1, 2]
                index.remove(face['face'])

                i = (1/(resolution + 1)) * (i + 1)
                j = (1/(resolution + 1)) * (j + 1)


                point[index[0]] += i - 0.5
                point[index[1]] += j - 0.5

                distance = Calc.distance(fromPos, point) + 1
                Player.getPlayer().lookAt(point[0], point[1], point[2])
                block = Player.rayTraceBlock(distance, False)
                Time.sleep(10)
                if block is None: continue
                blockPos = [block.getX(), block.getY(), block.getZ()]

                if opposite:
                    check = False
                    for face_ in faces:
                        if face_['neighbor'].pos == blockPos:
                            check = True

                    if not check: continue
                else:
                    if blockPos != self.pos: continue

                points.append(point[:])
                if earlyReturn: return points
            
        # Logger.debug(f'Points: {len(points)}/{(resolution)**2 * len(faces)}')
        # for point in points:
        #     Chat.say(f'/execute at @s run particle minecraft:flame {point[0]} {point[1]} {point[2]} 0 0 0 0 1 force')
        #     time.sleep(0.1)
        return points


    def getInteractPoint(self, fromPos: list = None, resolution: int = 3, 
                         solid: bool = False, opposite: bool = False,
                         earlyReturn: bool = False,
                         faces: list = None) -> list[float] | None:
        """Get the best interact point of a block"""
        if resolution < 2:
            raise ValueError('Resolution must be greater than 1')
    
        points = self.getVisiblePoints(fromPos, resolution, opposite=opposite, solid=solid, earlyReturn=earlyReturn, faces=faces)
        if len(points) == 0: return None

        grid = {}
        for point in points:
            x = math.floor(point[0] * resolution)
            y = math.floor(point[1] * resolution)
            z = math.floor(point[2] * resolution)
            if (x, y, z) not in grid:
                grid[(x, y, z)] = 0

            grid[(x, y, z)] += 1

        cell = max(grid, key=grid.get)
        center = [cell[0] / resolution, cell[1] / resolution, cell[2] / resolution]
        points.sort(key=lambda p: Calc.distance(p, center))
        point = points[0]
        return point


    @staticmethod
    def getBlock(pos: list[int], mask: dict = None) -> Block | None:
        """Get the block at a position"""
        if mask is None: mask = {}

        if encodePos(pos) in mask:
            return mask[encodePos(pos)]
        
        data = World.getBlock(pos[0], pos[1], pos[2])
    
        return Block(data.getBlockStateHelper(), pos) if data else None
    

    @staticmethod
    def createMaskBlock(pos: list[int], place: bool = True) -> Block:
        block = Block.getBlock(pos)
        if place:
            block.id = 'minecraft:stone'
            block.isAir = False
            block.isSolid = True
            block.isOpaque = True
            block.isLiquid = False
            block.isWater = False
            block.isLava = False
        else:
            block.id = 'minecraft:air'
            block.isAir = True
            block.isSolid = False
            block.isOpaque = False
            block.isLiquid = False
            block.isWater = False
            block.isLava = False

        return block
    
    @staticmethod
    def getLookAtBlock() -> Block | None:
        reach = Player.getReach()
        block = Player.rayTraceBlock(reach, True)

        if block is None:
            return None
        
        pos = block.getBlockPos()
        pos = [pos.getX(), pos.getY(), pos.getZ()]

        return Block.getBlock(pos)


class Node:
    """A node in the walk graph"""
    def __init__(self, parent: Node, position: list[int], weight: int = 1,
                mask: dict = None
        ):
        self.parent = parent
        self.pathPosition = 1 if parent is None else parent.pathPosition + 1 
        self.position = position
        self.weight = weight
        self.mask = mask if mask is not None else {}
        self.heuristic = None
        
        self.place = 0
        self.break_ = 0
        self.action = None

    def copy(self):
        """Return a copy of the node"""
        node = Node(self.parent, self.position, self.weight, self.mask)
        node.place = self.place
        node.break_ = self.break_
        return node

    def __eq__(self, other: Node):
        return self.position == other.position

    def __str__(self):
        return f"Node({self.position})"
    
    def __lt__(self, other: Node):
        if self.heuristic == other.heuristic:
            return self.pathPosition < other.pathPosition
        
        return self.heuristic < other.heuristic
    

class Walk:
    """A class that implements the A* pathfinding algorithm"""
    def __init__(self, startPos: list[int], endPos: list[int] | Region,
            maxJump: int = 1, maxFall: int = 5,
            canPlace: bool = True, canBreak: bool = True,
            allowListBreak: list[str] = None, denyListBreak: list[str] = None,
            reverse: bool = False, weightMask: float = 1.0,
            maxPathLength: int = 50,
            timeLimit: int = 5, saveExplorationMap: str = None,
            listener: callable = lambda: None
        ):
        """Create a new Walk instance
        startPos: the start position
        endPos: the end position or region
        maxJump: the maximum number of blocks that the player can jump
        maxFall: the maximum number of blocks that the player can fall
        canPlace: if the player can place blocks
        canBreak: if the player can break blocks
        allowListBreak: the list of blocks that the player can break
        denyListBreak: the list of blocks that the player can't break
        reverse: if the player are leaving the end region
        weightMask: the weight to each break and place action
        maxPathLength: the maximum distance of the path, if the path is longer than this, the search will be split in multiple searches
        timeLimit: the time limit to find the path in seconds
        saveExplorationMap: the file to save the exploration map, if None, don't save
        """

        if not isinstance(startPos, list): # Pos3D
            startPos = [startPos.x, startPos.y, startPos.z]

        if not isinstance(endPos, Region):
            if not isinstance(endPos, list): # Pos3D
                endPos = [endPos.x, endPos.y, endPos.z]
        
            endPos = [math.floor(endPos[0]), math.floor(endPos[1]), math.floor(endPos[2])]
            endPos = Region.createRegion(endPos, 1)
    

        self.start = [math.floor(startPos[0]), math.floor(startPos[1]), math.floor(startPos[2])]
        self.stepStart = self.start.copy()
        self.end = endPos
        self.stepEnd = self.end.copy()
        self.maxJump = maxJump
        self.maxFall = maxFall
        self.canPlace = canPlace
        self.canBreak = canBreak
        self.allowListBreak = allowListBreak if allowListBreak is not None else []
        self.denyListBreak = denyListBreak if denyListBreak is not None else []
        self.reverse = reverse
        self.weightMask = weightMask
        self.maxPathLength = maxPathLength
        self.timeLimit = timeLimit
        self.saveExplorationMap = saveExplorationMap
        self.listener = listener        
        self.placeBlocks = [
            'minecraft:planks', 'minecraft:cobblestone', 'minecraft:stone',
            'minecraft:grass_block', 'minecraft:dirt', 'minecraft:cobblestone',
        ]

        self.allowListBreak = [x for id in self.allowListBreak for x in Dictionary.getIds(id)]
        self.denyListBreak = [x for id in self.denyListBreak for x in Dictionary.getIds(id)]

        self.denyList = set() # list of positions that the player stucked
        self.explorationMap = {}
        
        self.__thread = None

        if self.saveExplorationMap is not None:
            self.explorationMap['start'] = self.start
            self.explorationMap['end'] = self.end.getBounds()
            self.explorationMap['path'] = []
            self.explorationMap['denyList'] = []
            self.explorationMap['openList'] = []
            self.explorationMap['closedList'] = []


    def getConfig(self) -> dict:
        """Get the config of the walk"""
        config = {}
        for attr in dir(self):
            if attr.startswith('__') or attr.startswith('_'): continue
            if callable(getattr(self, attr)): continue
            config[attr] = getattr(self, attr)

            if type(config[attr]) == set:
                config[attr] = list(config[attr]) # json doesn't support sets


        config['end'] = config['end'].getBounds()
        config['stepEnd'] = config['stepEnd'].getBounds()
        
        return config


    def setStep(self, startPos: list[int], endPos: list[int] | Region):
        """Reset the walk"""
        if not isinstance(startPos, list):
            startPos = [startPos.x, startPos.y, startPos.z]
        
        if not isinstance(endPos, Region):
            if not isinstance(endPos, list):
                endPos = [endPos.x, endPos.y, endPos.z]

            endPos =  [math.floor(endPos[0]), math.floor(endPos[1]), math.floor(endPos[2])]
            endPos = Region.createRegion(endPos, 1)
        
        self.stepStart = [math.floor(startPos[0]), math.floor(startPos[1]), math.floor(startPos[2])]
        self.stepEnd = endPos
        self.explorationMap['start'] = self.stepStart
        self.explorationMap['end'] = self.stepEnd.getBounds()
        self.explorationMap['path'] = []
        self.explorationMap['openList'] = []
        self.explorationMap['closedList'] = []


    def getWalkablePos(self, pos: list[int], _from: list[int], mask: dict = None) -> list[int] | None: 
        """Check if the position is walkable and return the position.
        If it is a position that has to be make a extra moviment, like jumping or falling,
        it will be necessary to return the position that the player will be after the moviment.
        If the position is not walkable, return None"""

        if mask is None: mask = {}

        for i in range(-self.maxFall, self.maxJump + 1):
            _pos = [pos[0], pos[1] + i, pos[2]]
            block = Block.getBlock(_pos, mask)
            if block is None: continue
            if block.isLava: continue
            
            # water
            if block.isWater:
                c = 0
                while True:
                    c += 1
                    _block = Block.getBlock([_pos[0], _pos[1] + c, _pos[2]], mask)
                    
                    if _block is None: return None
                    if _block.isSolid: return None
                    if _block.isWater: continue
                    if _block.isAir: return [_pos[0], _pos[1] + c, _pos[2]] # return the last water block
            
            # space to walk
            if block.isSolid: continue
            _block = Block.getBlock([_pos[0], _from[1] + 1, _pos[2]], mask)
            if ((_block is None) or (_block.isSolid)): continue 

            # diagonal space
            if pos[0] != _from[0] and pos[2] != _from[2]:
                _block = Block.getBlock([_pos[0], _from[1], _from[2]], mask)
                if (_block is None) or (_block.isSolid): continue
                _block = Block.getBlock([_pos[0], _from[1]+1, _from[2]], mask)
                if (_block is None) or (_block.isSolid): continue

                _block = Block.getBlock([_from[0], _from[1], _pos[2]], mask)
                if (_block is None) or (_block.isSolid): continue
                _block = Block.getBlock([_from[0], _from[1]+1, _pos[2]], mask)
                if (_block is None) or (_block.isSolid): continue

            # jump/fall
            passed = True
            if i < 0:
                for j in range(i, 1):
                    _block = Block.getBlock([_pos[0], _from[1] + j, _pos[2]], mask)
                    if (_block is None) or (_block.isSolid):
                        passed = False
                        break

            elif i > 0:
                for j in range(1, i+2):
                    _block = Block.getBlock([_from[0], _from[1] + j, _from[2]], mask)
                    if (_block is None) or (_block.isSolid):
                        passed = False
                        break

                _block = Block.getBlock([_pos[0],_pos[1],_pos[2]], mask)
                if (_block is None) or (_block.isSolid): passed = False
                
                _block = Block.getBlock([_pos[0],_pos[1]+1,_pos[2]], mask)
                if (_block is None) or (_block.isSolid): passed = False


            if not passed: continue
            # floor to walk
            _block = Block.getBlock([_pos[0], _pos[1] - 1, _pos[2]], mask)
            
            if (_block is None): continue
            if _block.isSolid: return _pos
            if _block.isWater: return _pos


    def neigbourPlaceUnder(self, node: Node) -> list[Node]:
        """Get the neighbours of a node that are place under nodes"""
        mask = node.mask.copy()

        block = Block.getBlock(node.position, mask)
        if not block.isSolid: return []
        if block.isWater: return [] # can place under water, but need to check if has a solid block in the base
        
        block = Block.createMaskBlock(node.position, place=True)
        mask[encodePos(node.position)] = block
        newPos = [node.position[0], node.position[1]+1, node.position[2]]
        pos = self.getWalkablePos(newPos, node.position, mask)
        if pos is not None:
            _node = Node(node, pos, mask=mask)
            _node.place = node.place + 1
            _node.action = {
                'type': 'place',
                'pos': node.position,
            }

            return [_node]
        return []


    def neigbourBreakUnder(self, node: Node) -> list[Node]:
        """Get the neighbours of a node that are break under nodes"""
        mask = node.mask.copy()
        newPos = [node.position[0], node.position[1]-1, node.position[2]]

        block = Block.getBlock(newPos, mask)

        if not block.isSolid: return []
        if block.id in self.denyListBreak: return []
        if self.allowListBreak and block.id not in self.allowListBreak: return []

        block = Block.createMaskBlock(newPos, place=False)
        mask[encodePos(newPos)] = block
        pos = self.getWalkablePos(newPos, node.position, mask)
        if pos is not None:
            _node = Node(node, pos, mask=mask)
            _node.break_ = node.break_ + 1
            _node.action = {
                'type': 'break',
                'pos': newPos,
            }

            return [_node]
        return []


    def neigbourBreak2Side(self, node: Node) -> list[Node]:
        """Get the neighbours of a node that are break side nodes"""
        # these nodes are not node movements, they are just to break blocks
        neighbours = []
        for x, z in itertools.product([-1, 0,  1], [-1, 0, 1]):
            if x==0 and z == 0: continue

            mask = node.mask.copy()

            pos = [node.position[0] + x, node.position[1], node.position[2] + z]
            pos1 = [node.position[0] + x, node.position[1] + 1, node.position[2] + z]

            block = Block.getBlock(pos, mask)
            block1 = Block.getBlock(pos1, mask)
            if not block.isSolid or not block1.isSolid: continue
            if block.id in self.denyListBreak or block1.id in self.denyListBreak: continue
            if self.allowListBreak:
                if block.id not in self.allowListBreak or block1.id not in self.allowListBreak: continue

            block = Block.createMaskBlock(pos, place=False)
            block1 = Block.createMaskBlock(pos1, place=False)
            
            mask[encodePos(pos)] = block
            mask[encodePos(pos1)] = block1

            newPos = self.getWalkablePos(pos, node.position, mask)
            if newPos is None: continue

            _node = Node(node, newPos, mask=mask)
            _node.break_ = node.break_ + 2
            _node.action = {
                'type': 'break',
                'pos': [pos, pos1],
            }
            neighbours.append(_node)

        return neighbours

            
    def getNeighbours(self, node: Node) -> list[Node]:
        """Get the neighbours of a node"""
        neighbours = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0: continue
                _pos = [node.position[0] + i, node.position[1], node.position[2] + j]
                pos = self.getWalkablePos(_pos, node.position, node.mask)
                if pos is None: continue
                _node = Node(node, pos, mask=node.mask)
                neighbours.append(_node)


        if self.canPlace:
            itemCount = Inv.countItem(self.placeBlocks)
            if itemCount - node.place > 0:
                nodes = self.neigbourPlaceUnder(node)
                neighbours.extend(nodes)

        if self.canBreak:
            # TODO: calculate the time to break the block and add to the heuristic
            nodes = self.neigbourBreakUnder(node)
            neighbours.extend(nodes)

            nodes = self.neigbourBreak2Side(node)
            neighbours.extend(nodes)            


        return neighbours


    def move(self, node: Node):
        """Basic move to the node position"""
        pos = node.position
        pos = [pos[0]+0.5, pos[1], pos[2]+0.5]
        Logger.debug(f"Moving to {pos}")
        
        if node.action is not None:
            Action.waitStop()
            if node.action['type'] == 'place':
                Action.placeBlock(node.action['pos'], self.placeBlocks, moveToPlace=False)
                
            if node.action['type'] == 'break':
                Logger.debug(f"Breaking {node.action['pos']}")
                Action.breakBlock(node.action['pos'])


        startTime = time.time()
        while True:
            self.listener()

            if time.time() - startTime > 3:
                raise Exception("Player stucked")
            
            actualPos = Player.getPlayer().getPos()
            actualPos = [actualPos.x, actualPos.y, actualPos.z]
            dist = Calc.distance(actualPos, pos)
            if dist < 0.5: break

            block = Block.getBlock([int(actualPos[0]), int(actualPos[1]), int(actualPos[2])])
            if block.isWater:
                while True:
                    self.listener()
                    if time.time() - startTime > 3:
                        raise Exception("Player stucked")
                    
                    actualPos = Player.getPlayer().getPos()
                    actualPos = [actualPos.x, actualPos.y, actualPos.z]        
                    dist2 = actualPos[1] - pos[1]
                    if dist2 > -0.5: break
    
                    KeyBind.pressKey("key.keyboard.space")
                    Client.waitTick(1)

                KeyBind.releaseKey("key.keyboard.space")

            elif pos[1] - actualPos[1] > 0.5:
                Action.jump()
                
            yaw = Player.getPlayer().getYaw()
            newYaw = math.degrees(math.atan2(pos[0] - actualPos[0], pos[2] - actualPos[2])) * -1
            diff = newYaw - yaw
            Player.moveForward(diff)
            Client.waitTick(1)
    

    def findPath(self) -> list[Node] | None:
        """Find a path from the start position to the end position"""
        startTime = time.time()

        startPos = self.stepStart
        endPos = self.stepEnd.getCenter()

        if self.stepEnd.contains(startPos) and not self.reverse: return []
        if not self.stepEnd.contains(startPos) and self.reverse: return []

        startNode = Node(None, startPos)
        endNode = Node(None, endPos)
        startNode.heuristic = self.heuristic(startNode, endNode)

        openList = [startNode]
        closedHash = set()
        openHash = set([encodePos(startNode.position)])

        while len(openList) > 0:
            self.listener()
            if time.time() - startTime > self.timeLimit: return None

            if self.saveExplorationMap is not None:
                self.explorationMap['openList'].append([node.position for node in openList])
                self.explorationMap['closedList'].append([decodePos(node) for node in closedHash])
                self.explorationMap['denyList'].append([decodePos(node) for node in self.denyList])
                self.saveMap()

            currentNode = openList.pop(0)
            openHash.remove(encodePos(currentNode.position))

            Logger.debug(f"Nodes in open list: {len(openList)} | time: {(time.time() - startTime):.2f} | pos: {currentNode}")

            if ((self.stepEnd.contains(currentNode.position) and not self.reverse)
                or (not self.stepEnd.contains(currentNode.position) and self.reverse)):
                path = []
                cell = currentNode
                while cell is not None:
                    path.append(cell)
                    cell = cell.parent
                
                if self.saveExplorationMap is not None:
                    self.explorationMap['path'] = [node.position for node in path[::-1]]
                    self.saveMap()

                return path[::-1]
            
            neighbours = self.getNeighbours(currentNode)
            for neighbour in neighbours:
                if encodePos(neighbour.position) in self.denyList: continue
                if encodePos(neighbour.position) in openHash: continue
                if encodePos(neighbour.position) in closedHash: continue

                neighbour.heuristic = self.heuristic(neighbour, endNode)
                
                index = Calc.binarySearchIndex(openList, neighbour)
                openList.insert(index, neighbour)
                openHash.add(encodePos(neighbour.position))
            
            closedHash.add(encodePos(currentNode.position))

        return None


    def searchClosestStep(self, pos: list[int], path: list[Node]) -> int:
        """Search the closest step node from a position in a path and return the index"""
        min_ = Calc.distance(path[0].position, pos)
        index = 0

        for i, node in enumerate(path[1:]):
            dist = Calc.distance(node.position, pos)

            if dist < min_:
                min_ = dist
                index = i + 1
        
        return index


    def followPath(self, path: list[Node]):
        """Follow a path"""
        for node in path:
            if len(path) > 2:
                dx = abs(node.position[0] - path[1].position[0])
                dy = abs(node.position[1] - path[1].position[1])
                dz = abs(node.position[2] - path[1].position[2])

                if ((dx==0 or dz==0) or (dx==2 and dz==2)) and dy==0:
                    # KeyBind.pressKeyBind("key.keyboard.shift")
                    ...

            self.move(node)
                
            # KeyBind.releaseKeyBind("key.keyboard.shift")


    def walk(self):
        """Find a path and follow it"""
        path = None

        lastPos = None
        lastPath = None
        while True:
            if path is None:
                pos = Player.getPlayer().getPos()
                pos = [pos.x, pos.y, pos.z]
    
            elif len(path) > 0:
                pos = path[-1].position[:]
            else:
                break

            dist = Calc.distance(pos, self.end.getCenter())
            
            if dist > self.maxPathLength and not self.reverse:
                end = self.end.getCenter()
                x, y, z = Calc.pointOnLine(pos, end, self.maxPathLength)
        
                size = self.maxPathLength / 10
                if size < 10: size = 10
        
                box = Region.createRegion([x, y, z], size)
                box.minPos[1] = -64
                box.maxPos[1] = 320

                self.setStep(pos, box)
            else:
                self.setStep(pos, self.end)

            path = self.findPath()
            if path is None:
                if self.__thread is not None:
                    self.__thread.join()

                raise PathNotFoundError("Path not found")

            if self.__thread is not None:
                self.__thread.join()
                self.__thread = None

                pos = Player.getPlayer().getPos()
                pos = [pos.x, pos.y, pos.z]
                dist = Calc.distance(pos, lastPos)
                index = self.searchClosestStep(pos, lastPath) + 1
                if index < len(lastPath):
                    Logger.debug(f'Len of last path: {len(lastPath)} | index: {index}')
                    Logger.debug(f'Adding {encodePos(lastPath[index].position)} to deny list')
                    self.denyList.add(encodePos(lastPath[index].position))
                    
                    Logger.debug('Path interrupted, recalculating...')
                    path = None
                    continue
            
            if len(path) == 0: continue

            lastPos = path[-1].position[:]
            lastPath = [node.copy() for node in path]

            Logger.debug("Path found")
            self.__thread = threading.Thread(target=self.followPath, args=(path,))
            self.__thread.start()

        Logger.debug("Path finished")


    def heuristic(self, node: Node, end: Node) -> float:
        """Calculate the heuristic cost of a node
        The heuristic cost is the distance from the node to the end node plus the length of the mask times the weightMask,
        multiplied by -1 if the path is reversed
        """
        w = -1 if self.reverse else 1
        return (Calc.distance(node.position, end.position) + len(node.mask) * self.weightMask + node.weight) * w


    def saveMap(self):
        """Save the exploration map"""
        if self.saveExplorationMap is None: return
        if self.saveExplorationMap is True: return
        with open(self.saveExplorationMap, 'w') as f:
            json.dump(self.explorationMap, f, indent=4)


    @staticmethod
    def walkTo(pos: Region | list[int], **kwargs) -> Walk:
        """Walk from the player position to a position"""

        walk = Walk(
            startPos=Player.getPlayer().getPos(),
            endPos=pos,
            listener=Script.scriptListener('walk'),
            **kwargs,
        )

        error = None
        try:
            walk.walk()
        except Exception as e:
            error = e
        finally:
            Script.stopScript('walk')

        if walk.__thread is not None:
            walk.__thread.join()

        if error is not None:
            raise error
        
        return walk
    

    @staticmethod
    def collectDrops(distance: int = 10, timeLimit: float = 0.5):
        """  Collect all drops in a distance  """
        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z]

        entities = World.getEntities(distance, 'item')
        entities = [e.getPos() for e in entities]
        entities.sort(key=lambda e: Calc.distance(pos, [e.x, e.y, e.z]))

        for e in entities:
            pos = [e.x, e.y, e.z]
            try:
                Walk.walkTo(pos, maxPathLength=distance*2, timeLimit=timeLimit)

            except PathNotFoundError:
                continue
