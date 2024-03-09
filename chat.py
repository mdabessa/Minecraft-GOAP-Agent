if __name__ == '':
    from JsMacrosAC import *


text = event.text.getString()
text = text.split('> ')[1]

Chat.log('Processing chat message: ' + text)
if text.startswith('!') and len(text) > 1:
    Chat.log('Detected command')
    fakeEvent = JsMacros.createCustomEvent('command')
    fakeEvent.putString('message', text[1:])
    JsMacros.runScript('commandHandler.py', fakeEvent)
