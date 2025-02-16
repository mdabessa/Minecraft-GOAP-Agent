GROUPS = {
    "minecraft:logs": [
        'minecraft:oak_log',
        'minecraft:birch_log',
        'minecraft:spruce_log',
        'minecraft:jungle_log',
        'minecraft:acacia_log',
        'minecraft:dark_oak_log',
        'minecraft:oak_logs',
        'minecraft:birch_logs',
        'minecraft:spruce_logs',
        'minecraft:jungle_logs',
        'minecraft:acacia_logs',
        'minecraft:dark_oak_logs',
        'minecraft:logs',
        'minecraft:log',
    ],

    "minecraft:planks": [
        'minecraft:oak_planks',
        'minecraft:birch_planks',
        'minecraft:spruce_planks',
        'minecraft:jungle_planks',
        'minecraft:acacia_planks',
        'minecraft:dark_oak_planks',
        'minecraft:planks',
        'minecraft:plank',
    ],
}

class Dictionary:
    @staticmethod
    def getGroup(name: str) -> str:
        """Get the group/tag of a item"""
        for group in GROUPS:
            if name in GROUPS[group]:
                return group
        
        return name

    @staticmethod
    def getIds(group: str) -> list:
        """Get all items in a group/tag"""
        if group in GROUPS:
            return GROUPS[group]
        else:
            return [group]
