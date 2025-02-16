import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.dictionary import Dictionary
    from libs.utils.logger import Logger



class NotEnoughItemsError(Exception):
    """Raised when there is not enough items."""
    pass


class Inv:
    """A class to handle the inventory"""
    hotbarSortMap = {
        'sword': 0,
        'pickaxe': 1,
        'axe': 2,
        'shovel': 3,
        'bow': 4,
        'food': 5,
        'building': 8,
    }

    tools = [
        'sword',
        'pickaxe',
        'axe',
        'shovel',
    ]
    

    @staticmethod
    def getBetterTool(pos: list[int]) -> str:
        """Get the better tool for breaking a block at pos"""
        pos = [math.floor(pos[0]), math.floor(pos[1]), math.floor(pos[2])]
        block = World.getBlock(pos[0], pos[1], pos[2])
        if block == None: return None

        inventory = Player.openInventory()
        player = Player.getPlayer()
        map = inventory.getMap()

        tools = []
        for tool in Inv.tools:
            item = inventory.getSlot(map['hotbar'][Inv.hotbarSortMap[tool]])
            if item == None: continue

            tool_ = {
                'id': Dictionary.getGroup(item.getItemId()),
                'level': Inv.getToolLevel(item.getItemId()),
                'tool': tool,
                'slot': map['hotbar'][Inv.hotbarSortMap[tool]],
                'timeToBreak': player.calculateMiningSpeed(item, block.getBlockStateHelper()),
            }
            tools.append(tool_)

        tools.sort(key=lambda x: x['timeToBreak'])
        if tools[0]['timeToBreak'] - tools[1]['timeToBreak'] > -0.1:
            # if the difference is less than 0.1s, the tool doesn't matter, 
            # return None to avoid to waste a wrong tool
            return None
        return tools[0]


    @staticmethod
    def sortHotbar():
        """Sort the hotbar"""
        inventory = Player.openInventory()
        map = inventory.getMap()
        itemSlot = None
        for item in Inv.hotbarSortMap:
            if item in Inv.tools:
                items = Inv.findTools(item)
                if len(items) == 0:
                    itemSlot = inventory.findFreeSlot('main')
                    itemSlot = int(itemSlot)
                else:
                    itemSlot = items[0]['slots'][0]

                if itemSlot == -1: # No free slot
                    nonTools = Inv.findNonTools() # avoid to waste a wrong tool
                    if len(nonTools) == 0:
                        continue

                    itemSlot = nonTools[0]['slots'][0]

            
            elif item == 'bow':
                _item = Inv.getItem(f'minecraft:bow')
                if _item is None: continue
                itemSlot = _item['slots'][0]

            elif item == 'food':
                continue # TODO: list of food
            
            else:
                continue
            
            if itemSlot is None: continue

            hotbarSlot = map['hotbar'][Inv.hotbarSortMap[item]]
            if itemSlot != hotbarSlot:
                inventory.swap(itemSlot, hotbarSlot)
                Time.sleep(100)

            Client.waitTick(1)

        inventory.close()


    @staticmethod
    def isTool(item: str, tool: str | list) -> bool:
        """Check if the item is a tool"""
        tool = [tool] if type(tool) == str else tool
        name = item.split('_')[-1] # minecraft:stone_pickaxe -> pickaxe
        return name in tool
    

    @staticmethod
    def findTools(tool: str) -> list: 
        """Find the tools in the inventory"""
        items = Inv.getItems()
        tools = []
        for item in items:
            if Inv.isTool(item['id'], tool):
                tools.append(item)
            
        tools.sort(key=lambda x: Inv.getToolLevel(x['id']), reverse=True)
        return tools


    @staticmethod
    def findNonTools(invMap: str = 'main') -> list:
        """Find the non tools in the main inventory"""

        inventory = Player.openInventory()
        map = inventory.getMap()
        nonTools = []

        for slot in map[invMap]:
            item = inventory.getSlot(slot)
            _item = {
                'id': Dictionary.getGroup(item.getItemId()),
                'slots': [slot],
                'count': item.getCount()
            }

            if Inv.isTool(_item['id'], Inv.tools): continue
            nonTools.append(_item)

        return nonTools


    @staticmethod
    def getToolLevel(tool_type: str) -> int:
        """Get the level of the tool"""
        if 'wood' in tool_type: return 1
        if 'stone' in tool_type: return 2
        if 'gold' in tool_type: return 2
        if 'iron' in tool_type: return 3
        if 'diamond' in tool_type: return 4
        if 'netherite' in tool_type: return 5
        return -1
    

    @staticmethod
    def countItems(parseGroups: bool = True) -> dict:
        """Count the number of items in the inventory"""
    
        inv = Player.openInventory()
        items = inv.getItemCount()
        if not parseGroups: return items
        
        count = {}
        for id in items:
            _id = Dictionary.getGroup(id)
            if _id not in count: count[_id] = 0
            count[_id] += items[id]

        return count

    @staticmethod
    def countItem(id: str | list, parseGroups: bool = True) -> int:
        """Count the number of items in the inventory"""
        if type(id) == str:
            id = [id]
        
        count = 0
        items = Inv.countItems(parseGroups)
        for _id in id:
            if _id in items:
                count += items[_id]

        return count

    @staticmethod
    def getItems(parseGroups: bool = True) -> list:
        """Get all items in the inventory"""
        inv = Player.openInventory()
        items = inv.getItems()
        slots = []
        for item in items:
            infos = {}
            id = item.getItemId()
            infos['id'] = Dictionary.getGroup(id) if parseGroups else id
            infos['count'] = item.getCount()
            _slots = inv.findItem(item.getItemId())
            infos['slots'] = list(_slots)
            slots.append(infos)
        
        return slots
    
    @staticmethod
    def getItem(id: str, parseGroups: bool = True) -> dict | None:
        """Get an item in the inventory"""
        items = Inv.getItems(parseGroups)
        for item in items:
            if item['id'] == id:
                return item
        
        return None
    
    @staticmethod
    def selectBuildingBlock(item: str = None) -> None:
        """Go to the building hotbar slot and if item is specified, select it"""
        inventory = Player.openInventory()
        if item is not None:
            i = Inv.getItem(item)
            map = inventory.getMap()
            itemSlot = i['slots'][0]
            hotbarSlot = map['hotbar'][Inv.hotbarSortMap['building']]
            if itemSlot != hotbarSlot:
                inventory.swap(itemSlot, hotbarSlot)
                Time.sleep(100)

        inventory.setSelectedHotbarSlotIndex(Inv.hotbarSortMap['building'])
        Client.waitTick(1)

    @staticmethod
    def selectTool(tool: str) -> int:
        """Go to the tool hotbar slot, select it and return the level of the tool"""
        if tool not in Inv.hotbarSortMap:
            raise Exception(f'Invalid tool {tool}')

        inventory = Player.openInventory()
        inventory.setSelectedHotbarSlotIndex(Inv.hotbarSortMap[tool])
        Client.waitTick(1)

        map = inventory.getMap()
        item = inventory.getSlot(map['hotbar'][Inv.hotbarSortMap[tool]])
        level = Inv.getToolLevel(item.getItemId())
        return level

    @staticmethod
    def selectNonTool() -> None:
        """Go to the non tool hotbar slot"""
        inventory = Player.openInventory()
        inventory.setSelectedHotbarSlotIndex(Inv.hotbarSortMap['food'])
        Client.waitTick(1)

    @staticmethod
    def getToolDurability(tool: str) -> int:
        """Get the tool health"""

        Inv.selectTool(tool)
        inventory = Player.openInventory()
        map = inventory.getMap()
        item = inventory.getSlot(map['hotbar'][Inv.hotbarSortMap[tool]])
        return item.getDurability()
    

    @staticmethod
    def getActualToolLevel(tool: str) -> int:
        """Get the actual tool level"""

        inventory = Player.openInventory()
        map = inventory.getMap()
        item = inventory.getSlot(map['hotbar'][Inv.hotbarSortMap[tool]])
        return Inv.getToolLevel(item.getItemId())
