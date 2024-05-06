import json
import os
import time
import traceback
import random
import math


if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Calc, Region
    from libs.inventory import Inv
    from libs.explorer import Explorer
    from libs.walk import Walk
    from libs.craft import Craft
    from libs.scripts import Script


testPath = os.path.join(
    os.getcwd(), 'config', 'jsMacros', 'Macros', 'tests', 'test.json')


def getEnvironment() -> dict:
    """Get the environment"""
    player = Player.getPlayer()
    pos = player.getPos()
    pos = (pos.x, pos.y, pos.z)

    env = {
        'player': {
            'name': player.getName().getString(),
            'pos': pos,
            'gamemode': Player.getGameMode(),
            'inventory': Inv.countItems(),
            # TODO: add state cache
            # TODO: add statistics, advancements, player status, etc.
        },
        'world': {
            'identifier': World.getWorldIdentifier(),
            'time': World.getTime(),
            'timeOfDay': World.getTimeOfDay(),
            'dimension': World.getDimension(),
            'biome': World.getBiome(),
            'difficulty': World.getDifficulty(),
            'weather': {
                'raining': World.isRaining(),
                'thundering': World.isThundering(),
                'isDay': World.isDay(),
                'isNight': World.isNight(),
                'moonPhase': World.getMoonPhase(),
            }
        },
        'client': {
            'version': Client.mcVersion(),
            'modLoader': Client.getModLoader(),
            'fps': Client.getFPS(),
        },
    }

    return env


def getTestReports() -> dict:
    """Get the test reports"""
    if os.path.exists(testPath):
        with open(testPath, 'r') as file:
            data = json.load(file)
    
        return data
    
    return {}


def clearTestReports():
    """Clear the test reports"""
    if os.path.exists(testPath):
        os.remove(testPath)


def saveTestReports(data: dict):
    """Save the test reports"""
    with open(testPath, 'w') as file:
        json.dump(data, file, indent=4)    


def testCase(func: callable) -> callable:
    def wrapper(*args, **kwargs):
        """The wrapper"""
        try:
            data = getTestReports()
            if func.__name__ not in data:
                data[func.__name__] = []

            data_ = {
                'args': args,
                'kwargs': kwargs,
                'startTimestamp': time.time(),
                'startEnvironment': getEnvironment(),
                'result': None,
                'error': None,
                'traceback': None,
            }

            try:
                result = func(*args, **kwargs)
                data_['result'] = result
            
            except Exception as e:
                data_['error'] = str(e)
                data_['traceback'] = traceback.format_exc()


            data_['endTimestamp'] = time.time()
            data_['duration'] = data_['endTimestamp'] - data_['startTimestamp']
            data_['endEnvironment'] = getEnvironment()
            data_['success'] = data_['error'] is None

            data[func.__name__].append(data_)
            saveTestReports(data)

        except Exception as e:
            Logger.error(f'Error in test wrapper: {e}')
            Logger.error(traceback.format_exc())
            raise e
    
        return result
    return wrapper
    

class Test:
    """Test class"""
    @staticmethod
    def waitPosLoad(pos: list, timeout: int = 15):
        """Wait for chunk load"""
        start = time.time()
        while True:
            if time.time() - start > timeout:
                raise Exception(f'The position {pos} takes too long to load [timeout: {timeout}]')
            
            block = World.getBlock(pos[0], pos[1], pos[2])
            if block is not None:
                break
            
            time.sleep(0.1)


    @staticmethod
    def resetEnvironment():
        """Reset the environment"""
        Chat.say('/gamemode creative')
        Chat.say('/clear')

        pos = Player.getPlayer().getPos()
        pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
        x = random.randint(1000, 10000)
        z = random.randint(1000, 10000)

        pos[0] += x
        pos[2] += z

        Chat.say(f'/tp {pos[0]} 500 {pos[2]}')

        # estimate the maxPathLength of Walk.walkTo
        # to wait for the chunk load
        # FIXME: get the maxPathLength from Walk.walkTo
        
        estimedMaxDistance = 110

        posLoad = Calc.pointOnLine(pos, [10**10, 200, 10**10], estimedMaxDistance)
        posLoad = [math.floor(posLoad[0]), math.floor(posLoad[1]), math.floor(posLoad[2])]
        Test.waitPosLoad(posLoad, estimedMaxDistance / 8) # 2 seconds per chunk
        time.sleep(1)

        floor = Explorer.getFloor(pos)
        Chat.say(f'/tp {floor[0]} {floor[1]+1} {floor[2]}')
        time.sleep(1)

        Chat.say('/gamemode survival')


    @staticmethod
    def getTest(name: str) -> callable:
        """Get a test by name"""
        tests = [x for x in dir(Test) if x.startswith('test')]
        for test in tests:
            if test.lower() == name.lower():
                return getattr(Test, test)
        
        return None


    @staticmethod
    @testCase
    def testWalk(distance: int = 500, *args, **kwargs) -> dict:
        """Test walk"""
        data = {
            'distance': distance,
            'args': args,
            'kwargs': kwargs,
        }
        error = None
        try:
            start = Player.getPlayer().getPos()
            start = [int(start.x), int(start.y), int(start.z)]

            end = [10**10, 0, 10**10]
            end = Calc.pointOnLine(start, end, distance)
            region = Region.createRegion(end, 16)
            
            Walk.walkTo(region, *args, **kwargs)

            data['start'] = start
            data['end'] = region.getBounds()
            Logger.print(f'TestWalk {Style.GREEN}success!')
        
        except Exception as e:
            Logger.print(f'TestWalk {Style.RED}failed!')
            error = e

        if error is not None:
            raise error

        return data


    @staticmethod
    @testCase
    def testCraft(item: str = 'minecraft:wooden_sword', *args, **kwargs) -> dict:
        """Test craft"""
        data = {
            'item': item,
            'args': args,
            'kwargs': kwargs,
        }
        
        listerner = Script.scriptListener('crafting')
        error = None
        try:
            Craft.craft(id=item, listener=listerner)
            Logger.print(f'TestCraft {Style.GREEN}success!')
        except Exception as e:
            Logger.print(f'TestCraft {Style.RED}failed!')
            error = e
        finally:
            Script.stopScript('crafting')

        if error is not None:
            raise error
    
        return data


    @staticmethod
    @testCase
    def testPathfinder(*args, ** kwargs) -> dict:
        """Test pathfinder"""
        data = {
            'args': args,
            'kwargs': kwargs,
        }

        error = None
        try:
            start = Player.getPlayer().getPos()
            start = [int(start.x), int(start.y), int(start.z)]
            
            end = [10**10, 0, 10**10]
            end = Calc.pointOnLine(start, end, 50)
            end1 = [end[0] + 10, -64, end[2] + 10]
            end2 = [end[0] - 10, 320, end[2] - 10]
            region = Region(end1, end2)

            walk = Walk(start, region, saveExplorationMap = True, *args, **kwargs)
            path = walk.findPath()
            if path is None:
                raise Exception('Path not found')

            data['start'] = start
            data['end'] = region.getBounds()
            data['pathLength'] = len(path)
            data['walkConfig'] = walk.getConfig()
            Logger.print(f'TestPathfinder {Style.GREEN}success!')

        except Exception as e:
            Logger.print(f'TestPathfinder {Style.RED}failed!')
            error = e

        if error is not None:
            raise error

        return data
