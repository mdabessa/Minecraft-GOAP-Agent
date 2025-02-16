from __future__ import annotations
import os
import threading
import time

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style, LoggerLevel
    from libs.scripts import Script
    from libs.state import State, Waypoint
    from libs.walk import Walk
    from libs.gathering.wood import Wood
    from libs.gathering.miner import Miner
    from libs.craft import Craft
    from libs.test import Test, clearTestReports


class CommandNotFound(Exception):
    """Raised when a command is not found."""
    pass

class CommandArgumentError(Exception):
    """Raised when a command argument is invalid."""
    pass


class Command:
    commands = []

    def __init__(self, name: str, func: callable, aliases: list = None, help: str = None):
        self.name = name
        self.func = func
        self.aliases = aliases if aliases is not None else []
        self.help = help if help is not None else 'No help provided'


    def execute(self, *args, **kwargs):
        """Execute the command."""
        self.func(*args, **kwargs)


    @staticmethod
    def getCommand(name: str) -> Command:
        """Get a command by name or alias."""
        for command in Command.commands:
            if (command.name == name or name in command.aliases):
                return command
        return None


    @staticmethod
    def command(name: str, aliases: list = None, help: str = None) -> callable:
        """Decorator to register a command."""
        def decorator(func: callable):
            command = Command(name, func, aliases, help)
            Command.commands.append(command)
            return func
        return decorator


@Command.command('help', aliases=['h'], help='Show help for commands')
def help(name: str = None, *args, **kwargs):
    if name is None:
        Logger.print(f'{Style.GOLD}Commands')
        for command in Command.commands:
            Logger.print(f'{Style.AQUA}{command.name} {Style.WHITE}{command.help}')
    else:
        command = Command.getCommand(name)
        if command is None:
            Logger.print(f'{Style.RED}Command {Style.AQUA}"{name}" {Style.RED}not found')
        else:
            Logger.print(f'{Style.GOLD}Help for command {Style.AQUA}"{command.name}"')
            Logger.print(f'{Style.AQUA}Description: {Style.WHITE}{command.help}')

            aliases = ', '.join([f'{Style.WHITE}<{Style.LIGHT_PURPLE}{alias}{Style.WHITE}>' for alias in command.aliases])
            Logger.print(f'{Style.AQUA}Aliases: {Style.WHITE}[{aliases}{Style.WHITE}]')
            
            args = ', '.join([f'{Style.WHITE}<{Style.LIGHT_PURPLE}{arg}{Style.WHITE}>' for arg in command.func.__code__.co_varnames[:command.func.__code__.co_argcount]])
            Logger.print(f'{Style.AQUA}Arguments: {Style.WHITE}[{args}{Style.WHITE}]')


@Command.command('stop', aliases=['s'], help='Stop all scripts')
def stop(*args, **kwargs):
    Script.stopAllScripts()
    Logger.print('All scripts stopped')


@Command.command('walk', aliases=['w', 'goto'], help='Walk to a position or waypoint')
def walk(*args, **kwargs):
    if len(args) == 1 or 'waypoint' in kwargs:
        name = args[0]
        wp = Waypoint.getWaypoint(name)
        
        if wp is None:
            raise CommandArgumentError(f'Waypoint "{name}" not found')

        if wp.dimension != World.getDimension():
            raise CommandArgumentError(f'Waypoint "{name}" is in another dimension')
            
        pos = [wp.x, wp.y, wp.z]
        objective = [float(x) for x in pos]

    else:
        try:
            x = args[0] if len(args) >= 1 else kwargs['x']
            y = args[1] if len(args) >= 2 else kwargs['y']
            z = args[2] if len(args) >= 3 else kwargs['z']

        except (IndexError, KeyError) as e:
            raise CommandArgumentError('Missing argument "x", "y" or "z"')

        objective = [float(x), float(y), float(z)]

    _kwargs = {}
    if 'save' in kwargs and bool(kwargs['save']):
        path = os.path.join(os.getcwd(), 'config', 'jsMacros', 'Macros')
        _kwargs['saveExplorationMap'] = path + '/explorationMap.json'
    
    Logger.print(f'Walking to {objective}')

    Walk.walkTo(objective, **_kwargs)

    pos = Player.getPlayer().getPos()
    pos = [pos.x, pos.y, pos.z]
    pos = [round(x, 2) for x in pos]
    Logger.print(f'Arrived at {pos}')


@Command.command('waypoint', aliases=['wp'], help='Create a waypoint')
def waypoint(subcommand: str = None, *args, **kwargs):
    if subcommand is None:
        Logger.print(f'{Style.GOLD}Subcommands')
        Logger.print(f'{Style.AQUA}create {Style.WHITE}Create a waypoint')
        Logger.print(f'{Style.AQUA}list {Style.WHITE}List all waypoints')
        Logger.print(f'{Style.AQUA}remove {Style.WHITE}Remove a waypoint')
        Logger.print(f'{Style.AQUA}tp {Style.WHITE}Teleport to a waypoint')
        return

    if subcommand == 'create':
        if  len(args) < 1 and 'name' not in kwargs:
            raise CommandArgumentError('Missing argument "name"')
        
        name = kwargs['name'] if 'name' in kwargs else args[0]

        if name.startswith('.'):
            raise CommandArgumentError(f'Waypoint name cannot start with "."')


        pos = Player.getPlayer().getPos()
        pos = [pos.x, pos.y, pos.z, World.getDimension()]

        if 'x' in kwargs: pos[0] = float(kwargs['x'])
        if 'y' in kwargs: pos[1] = float(kwargs['y'])
        if 'z' in kwargs: pos[2] = float(kwargs['z'])
        if 'd' in kwargs: pos[3] = kwargs['d']
        if 'dimension' in kwargs: pos[3] = kwargs['dimension']

        pos[0] = round(pos[0], 2)
        pos[1] = round(pos[1], 2)
        pos[2] = round(pos[2], 2)

        wp = Waypoint.addWaypoint(name, pos[0], pos[1], pos[2], pos[3])
        Logger.print(f'{wp} created')
    
    elif subcommand == 'list':
        waypoints = Waypoint.getWaypoints()
        Logger.print(f'{Style.GOLD}Waypoints')
        for name, wp in waypoints.items():
            if name.startswith('.') and not bool(kwargs.get('all', False)):
                continue
            Logger.print(f'{wp}')
    
    elif subcommand == 'remove':
        if 'name' not in kwargs and len(args) < 1:
            raise CommandArgumentError('Missing argument "name"')

        name = kwargs['name'] if 'name' in kwargs else args[0]

        wp = Waypoint.getWaypoint(name)
        if name is None:
            raise CommandArgumentError(f'Waypoint "{name}" not found')

        if name.startswith('.') and not bool(kwargs.get('all', False)):
            raise CommandArgumentError(f'Cannot remove waypoint "{name}", it is a system waypoint')

        wp.delete()

        Logger.print(f'Waypoint {Style.AQUA}"{name}" {Style.WHITE}removed')
    
    elif subcommand == 'tp':
        state = State()
        cheat = state.get('cheat', False)
        if not cheat:
            raise CommandArgumentError('Cheats are disabled')

        if len(args) < 1 and 'name' not in kwargs:
            raise CommandArgumentError('Missing argument "name"')
        
        name = kwargs['name'] if 'name' in kwargs else args[0]

        wp = Waypoint.getWaypoint(name)
        if wp is None:
            raise CommandArgumentError(f'Waypoint "{name}" not found')
        
        if wp['dimension'] != World.getDimension():
            raise CommandArgumentError(f'Waypoint "{name}" is in another dimension')
        
        text = f'/tp @p {pos["x"]} {pos["y"]} {pos["z"]}'
        Chat.say(text)

    else:
        raise CommandArgumentError(f'Unknown subcommand "{subcommand}"')


@Command.command('cheat', aliases=['c'], help='Enable or disable cheats')
def cheat(*args, **kwargs):
    state = State()
    cheat = state.get('cheat', False)
    if cheat:
        state.set('cheat', False)
        Logger.print('Cheats disabled')
    else:
        state.set('cheat', True)
        Logger.print('Cheats enabled')
    state.save()


@Command.command('script', aliases=['sc', 'scripts'], help='List all scripts')
def script(*args, **kwargs):
    scripts = Script.getScripts()
    Logger.print(f'{Style.GOLD}Scripts')
    for key, script in scripts.items():
        name = script['name']
        created = script['created']
        runningTime = time.time() - created
        Logger.print(f'{Style.AQUA}{name} {Style.WHITE}Running for {Style.GREEN}{runningTime:.2f}s')


@Command.command('craft', aliases=['cr'], help='Craft an item')
def craft(id: str = None, count: int = 1, *args, **kwargs):
    if id is None:
        Logger.print('Usage: craft <id> [count]')
        return
    
    if not id.startswith('minecraft:'):
        id = 'minecraft:' + id
    
    listerner = Script.scriptListener('crafting')
    error = None
    try:
        Craft.craft(id=id, count=int(count), listener=listerner)
        Logger.print(f'Crafted {count}x {id}')
    except Exception as e:
        error = e
    finally:
        Script.stopScript('crafting')

    if error is not None:
        raise error


@Command.command('test', aliases=['t'], help='Run a test')
def test(testName: str = None, 
        quantity: int = 1, timeoutSec: int = 240,
        *args, **kwargs):
    """Run a test"""
    timeoutSec = int(timeoutSec)

    if testName is None:
        Logger.print('Usage: test <testName>')
        return

    test = Test.getTest(testName)
    if test is None:
        raise CommandArgumentError(f'Test "{testName}" not found')

    if 'maxPathLength' in kwargs and int(kwargs['maxPathLength']) > 200:
        # The maxPathLength argument cannot be greater than 200
        # because when the test is reset, the player is teleported
        # and it takes some time to load the chunks.
        raise CommandArgumentError('maxPathLength cannot be greater than 200')


    quantity = int(quantity)

    listener = Script.scriptListener('test')
    error = None
    thread = None

    # Run the test 'quantity' times.
    # If the test takes more than 'timeoutSec' seconds, stop all scripts,
    # except the test script.
    # If the listener was fired to stop the test handler, stop all scripts.
    Logger.print(f'Running test {Style.AQUA}"{testName}"{Style.WHITE} {quantity} times')
    try:
        for i in range(quantity):
            Logger.print(f'Running test {Style.AQUA}"{testName}"{Style.WHITE} {i + 1}/{quantity}')
            Test.resetEnvironment()

            thread = threading.Thread(target=test, args=args, kwargs=kwargs)
            thread.start()
            start = time.time()
            while thread.is_alive():
                time.sleep(0.1)
                listener()
                if time.time() - start > timeoutSec:
                    Logger.print(f'The test {Style.AQUA}"{testName}"{Style.WHITE} took too long to finish ({Style.RED}{timeoutSec}s{Style.WHITE})')
                    Script.stopAllScriptsExcept('test')
                    break
                
            thread.join()
    
    except Exception as e:
        error = e

    finally:
        Script.stopAllScripts()
        if thread is not None:
            thread.join() # Wait for the thread to finish

    Chat.say('/gamemode creative')

    if error is not None:
        Logger.error(f'The test handler crashed')
        raise error

    Logger.print(f'Test {Style.AQUA}"{testName}"{Style.WHITE} finished')


@Command.command('clearTest', aliases=['ct'], help='Clear the tests data')
def clearTest(*args, **kwargs):
    clearTestReports()
    Logger.print('Tests data cleared')


@Command.command('rndTp', help='Teleport to a random position')
def rndTp(*args, **kwargs):
    Test.randomTP()
    pos = Player.getPlayer().getPos()
    
    Logger.print(f'Teleported to {Style.AQUA}{pos.x} {pos.y} {pos.z}')


@Command.command('gatherWood', aliases=['gw'], help='Gather wood')
def gatherWood(quantity: int = 1, exploreIfNoWood: bool = True, *args, **kwargs):
    quantity = int(quantity)

    if quantity <= 0:
        raise CommandArgumentError('quantity must be greater than 0')

    Logger.print(f'Gathering {quantity} wood')

    Wood.gatherWood(quantity=quantity, exploreIfNoWood=exploreIfNoWood)

    Logger.print(f'Gathered!')

@Command.command('mine', help='Mine macro')
def mine(*args, **kwargs):
    Miner.mine()
