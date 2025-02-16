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

    "minecraft:leaves": [
        'minecraft:oak_leaves',
        'minecraft:birch_leaves',
        'minecraft:spruce_leaves',
        'minecraft:jungle_leaves',
        'minecraft:acacia_leaves',
        'minecraft:dark_oak_leaves',
        'minecraft:mangrove_leaves',
        'minecraft:cherry_leaves',
        'minecraft:azalea_leaves',
        'minecraft:flowering_azalea_leaves',
    ],

    "minecraft:saplings": [
        'minecraft:oak_sapling',
        'minecraft:birch_sapling',
        'minecraft:spruce_sapling',
        'minecraft:jungle_sapling',
        'minecraft:acacia_sapling',
        'minecraft:dark_oak_sapling',
        'minecraft:mangrove_sapling',
        'minecraft:cherry_sapling',
    ],

    "minecraft:dirt": [
        'minecraft:dirt',
        'minecraft:dirt_path',
        'minecraft:coarse_dirt',
        'minecraft:rooted_dirt',
        'minecraft:grass_block',
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
