"""
A handler for commands sent by the chat
"""

from libs.importer import require

if __name__ == '':
    from JsMacrosAC import *
    from libs.commands import Command, CommandNotFound


require('__all__', globals())

Client.waitTick(1)
message = event.getString('message')
if message is not None:
    cmd = message.split(' ')[0]
    args = message.split(' ')[1:]

    kwargs = {x.split('=')[0]: x.split('=')[1] for x in args if '=' in x}
    args = [x for x in args if '=' not in x]

    command = Command.getCommand(cmd)
    if command is None:
        raise CommandNotFound(f'Command "{cmd}" not found')
    else:
        command.execute(*args, **kwargs)
