if __name__ == '':
    from JsMacrosAC import *


if event.message.startswith('!') and len(event.message) > 1:
    fakeEvent = JsMacros.createCustomEvent('command')
    fakeEvent.putString('message', event.message[1:])
    JsMacros.runScript('commandHandler.py', fakeEvent)
