# Minecraft GOAP Agent
An implementation of the GOAP and Pathfinding algorithm in Minecraft 1.20 using the mod [JsMacros](https://github.com/JsMacros/JsMacros) with JEP extension.

## How to use
1. Install [JsMacros](https://www.curseforge.com/minecraft/mc-mods/jsmacros)
2. Install [JEP](https://jsmacros.wagyourtail.xyz/?/extensions.html)
3. Extract the recipes files from the minecraft jar file and put them in the `recipes` folder
4. Set the `chat.py` file to run on ChatEvent in JsMacros settings

## How it works
Using the GOAP algorithm, the agent will try to make the recipes and collect the items needed to make the recipes. If the agent doesn't have the items needed to make the recipe, it will make all the recipes that are needed recursively.
The agent uses the A* algorithm to find the path to move in the world. The pathfinding algorithm can break and place blocks to move.
To collect the items, the agent mines ores and trees and it will craft the tools needed to the collection.

## Commands
- `!help`: Show the help message
- `!stop`: Stop all scripts running
- `!walk <pos>`: Walk to the position or waypoint using the A* algorithm
- `!waypoint <*args>`: Manage the waypoints that can be used in the `!walk` command
- `!cheat`: Toggle the cheat flag that allows the agent to teleport to waypoints
- `!script`: List all scripts running
- `!craft <item_id>`: Craft or collect an item using the GOAP algorithm
- `!test <test_name> <*args>`: Run a test script registered

## Version
- Minecraft: 1.20.2
- Python: 3.11
