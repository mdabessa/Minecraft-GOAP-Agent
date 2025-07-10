from libs.importer import require, LIBS
import time

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.logger import Logger


def waitFish():
    while True:
        controller = GlobalVars.getBoolean("fishing")
        if not controller: break
        
        entities = World.getEntities(10)
        
        entities = [entity for entity in entities if entity.getType() == 'minecraft:fishing_bobber']
        if len(entities) == 0: return
        fishing_bobber = entities[0]

        nbt = fishing_bobber.getNBT()
        fall_distance = nbt.get('FallDistance').asFloat()
        if fall_distance > 0.13:
            KeyBind.pressKeyBind('key.use')
            Client.waitTick(1)
            KeyBind.releaseKeyBind('key.use')
            return

        Client.waitTick(1)


controller = GlobalVars.getBoolean("fishing")

if controller is None: controller = True
else: controller = not controller

GlobalVars.toggleBoolean("fishing")

Logger.print(f'[Fishing] script {"enabled" if controller else "disabled"}!')

player = Player.getPlayer()
yaw = player.getYaw()
pitch = player.getPitch()

while controller:
    controller = GlobalVars.getBoolean("fishing")
    if not controller: break

    player.lookAt(yaw, pitch)
    KeyBind.pressKeyBind('key.use')
    Client.waitTick(1)
    KeyBind.releaseKeyBind('key.use')
    Time.sleep(3000)
    waitFish()


if controller:
    GlobalVars.toggleBoolean("fishing")