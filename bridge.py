from libs.importer import require, LIBS
import time
import math

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.walk import Block
    from libs.inventory import Inv




scriptName = 'main'
controller = GlobalVars.getBoolean(scriptName)
if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean(scriptName)
Chat.log(f'Main script {"enabled" if controller else "disabled"}!')

id = 'minecraft:glass'
yaw = 180
pitch = 78

pos = Player.getPlayer().getPos()
pos = [math.floor(pos.x), math.floor(pos.y)-1, math.floor(pos.z)]
block = Block.getBlock(pos)
timeLast = time.time()
while controller:
    controller = GlobalVars.getBoolean(scriptName)
    if not controller: break

    player = Player.getPlayer()

    if not player.isSneaking():
        KeyBind.keyBind('key.sneak', True)

    if 'key.keyboard.s' not in KeyBind.getPressedKeys():
        KeyBind.key('key.keyboard.s', True)

    Inv.selectBuildingBlock(id)

    Client.waitTick(1)
    player.lookAt(yaw, pitch)
    Client.waitTick(1)

    KeyBind.pressKeyBind('key.use')
    Client.waitTick(1)
    KeyBind.releaseKeyBind('key.use')
    Client.waitTick(1)

    pos = player.getPos()
    pos = [math.floor(pos.x), math.floor(pos.y)-1, math.floor(pos.z)]
    block_ = Block.getBlock(pos)

    if block.pos == block_.pos and time.time() - timeLast > 2:
        Chat.log('Mudando de direção')
        key = 'key.keyboard.a' if yaw == 180 else 'key.keyboard.d'

        KeyBind.key("key.keyboard.s", False)
        while True:
            controller = GlobalVars.getBoolean(scriptName)
            if not controller: break

            new_pos = Player.getPlayer().getPos()
            new_pos = [math.floor(new_pos.x), math.floor(new_pos.y)-1, math.floor(new_pos.z)]

            if new_pos != pos:
                Client.waitTick(10)
                break

            KeyBind.key(key, True)
            Client.waitTick(1)
            Chat.log(KeyBind.getPressedKeys())
        
        KeyBind.key(key, False)
        Client.waitTick(1)
        yaw = 0 if yaw == 180 else 180

    elif block.pos != block_.pos:
        timeLast = time.time()
        block = block_


KeyBind.keyBind("key.sneak", False)
KeyBind.key("key.keyboard.s", False)
KeyBind.key("key.keyboard.a", False)
KeyBind.key("key.keyboard.d", False)
if controller:
    GlobalVars.toggleBoolean(scriptName)
