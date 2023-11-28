from __future__ import annotations
import os
import threading
import time

if __name__ == '':
    from JsMacrosAC import *
    from libs.scripts import Script
    from libs.state import State
    from libs.walk import Walk
    from libs.craft import Craft
    from libs.test import Test


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
        Chat.log('Commands:')
        for command in Command.commands:
            Chat.log(f'  {command.name} - {command.help}')
    else:
        command = Command.getCommand(name)
        if command is None:
            Chat.log(f'Command "{name}" not found')
        else:
            Chat.log(f'Help for command "{command.name}":')
            Chat.log(f'  {command.help}')
            Chat.log(f'  Aliases: {command.aliases}')
            args = ', '.join([f'<{arg}>' for arg in command.func.__code__.co_varnames[:command.func.__code__.co_argcount]])
            Chat.log(f'  Arguments: {args}')


@Command.command('stop', aliases=['s'], help='Stop all scripts')
def stop(*args, **kwargs):
    Script.stopAllScripts()
    Chat.log('All scripts stopped')


@Command.command('walk', aliases=['w', 'goto'], help='Walk to a position or waypoint')
def walk(*args, **kwargs):
    if len(args) == 1 or 'waypoint' in kwargs:
        name = args[0]
        state = State()
        waypoints = state.get('waypoints', {})
        
        if name not in waypoints:
            raise CommandArgumentError(f'Waypoint "{name}" not found')

        if waypoints[name][3] != World.getDimension():
            raise CommandArgumentError(f'Waypoint "{name}" is in another dimension')
            
        pos = waypoints[name][:3]
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
    
    Walk.walkTo(objective, **_kwargs)


@Command.command('waypoint', aliases=['wp'], help='Create a waypoint')
def waypoint(subcommand: str = None, *args, **kwargs):
    if subcommand is None:
        Chat.log('Subcommands:')
        Chat.log('  create - Create a waypoint')
        Chat.log('  list - List all waypoints')
        Chat.log('  remove - Remove a waypoint')
        Chat.log('  tp - Teleport to a waypoint')
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

        state = State()
        waypoints = state.get('waypoints', {})
        waypoints[name] = pos
        state.set('waypoints', waypoints)
        state.save()

        Chat.log(f'Waypoint [{name}](x={pos[0]}, y={pos[1]}, z={pos[2]}, dimension={pos[3]}) created')
    
    elif subcommand == 'list':
        state = State()
        waypoints = state.get('waypoints', {})
        Chat.log('Waypoints:')
        for name, pos in waypoints.items():
            if name.startswith('.') and not bool(kwargs.get('all', False)):
                continue

            Chat.log(f'  {name} - (x={pos[0]}, y={pos[1]}, z={pos[2]}, dimension={pos[3]})')
    
    elif subcommand == 'remove':
        if 'name' not in kwargs and len(args) < 1:
            raise CommandArgumentError('Missing argument "name"')

        name = kwargs['name'] if 'name' in kwargs else args[0]

        state = State()
        waypoints = state.get('waypoints', {})
        if name not in waypoints:
            raise CommandArgumentError(f'Waypoint "{name}" not found')

        if name.startswith('.') and not bool(kwargs.get('all', False)):
            raise CommandArgumentError(f'Cannot remove waypoint "{name}", it is a system waypoint')

        del waypoints[name]
        state.set('waypoints', waypoints)
        state.save()

        Chat.log(f'Waypoint "{name}" removed')
    
    elif subcommand == 'tp':
        state = State()
        cheat = state.get('cheat', False)
        if not cheat:
            raise CommandArgumentError('Cheats are disabled')

        if len(args) < 1 and 'name' not in kwargs:
            raise CommandArgumentError('Missing argument "name"')
        
        name = kwargs['name'] if 'name' in kwargs else args[0]

        waypoints = state.get('waypoints', {})
        if name not in waypoints:
            raise CommandArgumentError(f'Waypoint "{name}" not found')
        
        pos = waypoints[name]
        if pos[3] != World.getDimension():
            raise CommandArgumentError(f'Waypoint "{name}" is in another dimension')
        
        text = f'/tp @p {pos[0]} {pos[1]} {pos[2]}'
        Chat.say(text)

    else:
        raise CommandArgumentError(f'Unknown subcommand "{subcommand}"')


@Command.command('cheat', aliases=['c'], help='Enable or disable cheats')
def cheat(*args, **kwargs):
    state = State()
    cheat = state.get('cheat', False)
    if cheat:
        state.set('cheat', False)
        Chat.log('Cheats disabled')
    else:
        state.set('cheat', True)
        Chat.log('Cheats enabled')
    state.save()


@Command.command('script', aliases=['sc', 'scripts'], help='List all scripts')
def script(*args, **kwargs):
    scripts = Script.getScripts()
    Chat.log('Scripts:')
    for script in scripts:
        name = script['name']
        created = script['created']
        runningTime = time.time() - created
        Chat.log(f'  {name} - {runningTime:.2f}s')


@Command.command('craft', aliases=['cr'], help='Craft an item')
def craft(id: str = None, count: int = 1, *args, **kwargs):
    if id is None:
        Chat.log('Usage: craft <id> [count]')
        return
    
    if not id.startswith('minecraft:'):
        id = 'minecraft:' + id
    
    listerner = Script.scriptListener('crafting')
    error = None
    try:
        Craft.craft(id=id, count=int(count), listener=listerner)
        Chat.log(f'Crafted {count}x {id}')
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

    if testName is None:
        Chat.log('Usage: test <testName>')
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
    Chat.log(f'Running test "{testName}" {quantity} times')
    try:
        for i in range(quantity):
            Chat.log(f'Running test {i + 1}/{quantity}...')
            Test.resetEnvironment()

            thread = threading.Thread(target=test, args=args, kwargs=kwargs)
            thread.start()
            start = time.time()
            while thread.is_alive():
                time.sleep(0.1)
                listener()
                if time.time() - start > timeoutSec:
                    Chat.log(f'The test "{testName}" took too long to finish [timeout: {timeoutSec}s]')
                    Script.stopAllScriptsExcept('test')
                    break
                
            thread.join()
    
    except Exception as e:
        error = e

    finally:
        Script.stopAllScripts()
        if thread is not None:
            thread.join() # Wait for the thread to finish

    if error is not None:
        Chat.log(f'The test handler crashed')
        raise error

    Chat.log(f'Test "{testName}" finished')
