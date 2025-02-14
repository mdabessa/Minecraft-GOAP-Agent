if __name__ == "":
    from JsMacrosAC import Client, KeyBind

import time

to_fov = 10
tick_per_sec = 20
key = 'key.keyboard.c'

config = Client.getGameOptions()
fov = config.getFov()

# Zoom in
steps = 10
for i in range(steps):
    config.setFov(int(fov + (to_fov - fov) * i / steps))
    time.sleep((5/tick_per_sec) / tick_per_sec)

config.setFov(to_fov)

# Wait for the key to be released
while True:
    keys = KeyBind.getPressedKeys()
    if not key in keys:
        break

    Client.waitTick()

# Zoom out
for i in range(steps):
    config.setFov(int(to_fov + (fov - to_fov) * i / steps))
    time.sleep((5/tick_per_sec) / tick_per_sec)

# Ensure the fov is reset
config.setFov(fov)
