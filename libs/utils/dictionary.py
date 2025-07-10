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
    'minecraft:stone_tool_materials': [
        'minecraft:cobblestone',
        'minecraft:blackstone',
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

    "minecraft:concrete": [
        'minecraft:white_concrete',
        'minecraft:orange_concrete',
        'minecraft:magenta_concrete',
        'minecraft:light_blue_concrete',
        'minecraft:yellow_concrete',
        'minecraft:lime_concrete',
        'minecraft:pink_concrete',
        'minecraft:gray_concrete',
        'minecraft:light_gray_concrete',
        'minecraft:cyan_concrete',
        'minecraft:purple_concrete',
        'minecraft:blue_concrete',
        'minecraft:brown_concrete',
        'minecraft:green_concrete',
        'minecraft:red_concrete',
        'minecraft:black_concrete',
    ],

    "minecraft:concrete_powder": [
        'minecraft:white_concrete_powder',
        'minecraft:orange_concrete_powder',
        'minecraft:magenta_concrete_powder',
        'minecraft:light_blue_concrete_powder',
        'minecraft:yellow_concrete_powder',
        'minecraft:lime_concrete_powder',
        'minecraft:pink_concrete_powder',
        'minecraft:gray_concrete_powder',
        'minecraft:light_gray_concrete_powder',
        'minecraft:cyan_concrete_powder',
        'minecraft:purple_concrete_powder',
        'minecraft:blue_concrete_powder',
        'minecraft:brown_concrete_powder',
        'minecraft:green_concrete_powder',
        'minecraft:red_concrete_powder',
        'minecraft:black_concrete_powder',
    ],
    'minecraft:torch': [
        'minecraft:torch',
        'minecraft:wall_torch',
    ],
    'minecraft:coal': [
        'minecraft:coal',
        'minecraft:charcoal',
    ]
}

class Dictionary:
    def getGroup(name: str) -> str:
        """Get the group/tag of a item"""
        for group in GROUPS:
            if name in GROUPS[group]:
                return group
        
        return name

    def getIds(group: str) -> list:
        """Get all items in a group/tag"""
        if group in GROUPS:
            return GROUPS[group]
        else:
            return [group]
