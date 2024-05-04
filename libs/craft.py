from __future__ import annotations
import json
import os
import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style
    from libs.utils.calc import Region, Calc
    from libs.utils.dictionary import Dictionary
    from libs.state import State, Waypoint
    from libs.inventory import Inv
    from libs.actions import Action, BlockNotVisibleError
    from libs.walk import Walk
    from libs.explorer import Explorer



recipes_path = os.path.join(os.getcwd(), 'config', 'jsMacros', 'Macros', 'recipes')

class NotCollectable(Exception):
    """Raised when the recipe is not collectable"""
    pass


class CraftingError(Exception):
    """Raised when a generic crafting error occurs"""
    pass


class Recipe:
    """A class to handle recipes"""
    def __init__(self, recipe: dict):
        self.recipe: dict = recipe
        
        self.type: str = recipe['type']
        self.result: dict = recipe['result']

        if type(self.result) is str:
            self.result = {'item': self.result, 'count': 1}
        
        if 'count' not in self.result:
            self.result['count'] = 1

        self.category: str | None = recipe.get('category', None)
        self.group: str | None = recipe.get('group', None)
        self.key: dict | None = recipe.get('key', None)
        self.pattern: list[str] | None = recipe.get('pattern', None)
            
        self.showNotification: bool = recipe.get('show_notification', False)
        self.ingredients: list[dict] = recipe.get('ingredients', [])
        
        if 'ingredient' in recipe:
            self.ingredients.append(recipe['ingredient'])
        
        if len(self.ingredients) == 0 and self.pattern is not None:
            ingredients = []
            for row in self.pattern:
                for char in row:
                    if char == ' ': continue
                    ingredients.append(self.key[char])
            self.ingredients = ingredients

        self.count: int = self.result['count']
        self.cookingTime: int = recipe.get('cookingtime', None)
        self.experience: float = recipe.get('experience', None)
        self.addition: dict | None = recipe.get('addition', None)
        self.base: dict | None = recipe.get('base', None)
        self.template: dict | None = recipe.get('template', None)

        self.name: str = self.result['item'] + ' x' + str(self.result['count']) + ' (' + self.type + ')'

    def getShape(self) -> list[int]:
        """Get the shape of the recipe"""
        
        if self.pattern is None: return [1]
        shape = [len(self.pattern)]
        if len(self.pattern) > 0:
            shape.append(len(self.pattern[0]))

        return shape

    def canCraftInHand(self) -> bool:
        """Check if the recipe can be crafted in hand"""
        if 'crafting' not in self.type: return False
        return max(self.getShape()) <= 2

    def countIngredients(self, quantity: int = 1) -> dict[str, int]:
        """Count the ingredients needed for the recipe"""
        count = {}
        for ingredient in self.ingredients:
            if 'item' in ingredient:
                id = ingredient['item']
            elif 'tag' in ingredient:
                id = ingredient['tag']
            else:
                raise ValueError('Ingredient must have item or tag')

            id = Dictionary.getGroup(id)
            if id not in count:
                count[id] = 0
            count[id] += 1

        for id in count:
            count[id] *= quantity
            count[id] /= self.count
            count[id] = math.ceil(count[id])

        return count

    def __str__(self) -> str:
        return self.name


class Craft:
    """A class to handle crafting"""
    recipes = []
    collectionMethods = {}
    interactionDelay = 100 # ms, minimum 10, lower can cause bugs


    @staticmethod
    def getCraftingPlace() -> list | None:
        """Get the position of the crafting table"""
        craftingTable =  World.findBlocksMatching('minecraft:crafting_table', 1)
        craftingTable = [[int(b.x), int(b.y), int(b.z)] for b in craftingTable]
        
        wp = Waypoint.getWaypoint('.crafting')
        if wp is not None:
            craftingTable.append([wp.x, wp.y, wp.z])
        
        pos = Player.getPlayer().getPos()
        pos = [int(pos.x), int(pos.y), int(pos.z)]
        craftingTable.sort(key=lambda b: Calc.distance(pos, b))

        if len(craftingTable) == 0: return None        
        pos = craftingTable[0]

        Craft.setCraftingPlace(pos)

        return pos


    @staticmethod
    def setCraftingPlace(pos: list):
        """Set the position of the crafting table"""
        dimention = World.getDimension()
        Waypoint.addWaypoint('.crafting', *pos, dimention)
        Logger.debug('Crafting table set at ' + str(pos))

    @staticmethod
    def resetCraftingPlace():
        """Reset the position of the crafting table"""
        Waypoint.delWaypoint('.crafting')
        Logger.debug('Crafting table reset')


    @staticmethod
    def buildCraftingTable():
        """Find a place and build a crafting table"""
        items = Inv.countItems()
        count = items.get('minecraft:crafting_table', 0)
        if count <= 0:
            Craft.craft(id='minecraft:crafting_table', count=1)

        places = Explorer.searchGoodPlaceToBuild(radius=16)

        while True:
            if len(places) == 0:
                # TODO: Implement a exploration algorithm to find a place to build a crafting table
                raise CraftingError('No place found to build a crafting table')

            pos = Player.getPlayer().getPos()
            pos = [int(pos.x), int(pos.y), int(pos.z)]
            places.sort(key=lambda p: Calc.distance(pos, p))
            place = places.pop(0)

            try:
                region = Region.createRegion(place, 3)
                Walk.walkTo(region)
                Action.placeBlock(place, 'minecraft:crafting_table')
                Craft.setCraftingPlace(place)
                Time.sleep(Craft.interactionDelay)
                break
            except BlockNotVisibleError:
                Logger.info('Failed to build a crafting table at ' + str(place))


    @staticmethod
    def collectionMethod(id: str | list[str]) -> callable:
        """Add a collection method"""
        def decorator(func: callable):
            if type(id) is str:
                Craft.collectionMethods[id] = func
            else:
                for i in id:
                    Craft.collectionMethods[i] = func
            return func

        return decorator


    @staticmethod
    def getRecipes(id: str) -> list[Recipe]:
        """Get all recipes for an item id"""
        recipes = []
        for r in Craft.getAllRecipes():
            if r.result['item'] == id:
                recipes.append(r)
            elif r.addition is not None and r.addition['item'] == id:
                recipes.append(r)
            elif r.group == id.replace('minecraft:', ''):
                recipes.append(r)

        return recipes


    @staticmethod
    def getAllRecipes() -> list[Recipe]:
        """Get all recipes"""
        if len(Craft.recipes) > 0: return Craft.recipes

        recipes = os.listdir(recipes_path)
        for r in recipes:
            if not r.endswith('.json'): continue
            with open(os.path.join(recipes_path, r)) as f:
                recipe = json.load(f)
                if 'result' not in recipe: continue

                recipe = Recipe(recipe)
                Craft.recipes.append(recipe)

        return Craft.recipes


    @staticmethod
    def goToCraftingTable():
        """Go to the crafting table"""
        c = 0
        while True:
            c += 1
            if c > 2: raise CraftingError('No crafting table found')
    
            place = Craft.getCraftingPlace()
            pos = Player.getPlayer().getPos()
            pos = [int(pos.x), int(pos.y), int(pos.z)]

            if place is None:
                Craft.buildCraftingTable()
                Logger.info('Crafting table built')
                place = Craft.getCraftingPlace()
            
            elif Calc.distance(pos, place) > 350:
                Craft.resetCraftingPlace()
                Logger.info('Crafting table too far, building a new one')
                continue
            
            # TODO: check if its better to walk to the crafting table or craft a new one

            region = Region.createRegion(place, 3)
            Walk.walkTo(region)

            pos = Player.getPlayer().getPos()
            pos = [int(pos.x), int(pos.y), int(pos.z)]

            craftingTable =  World.findBlocksMatching('minecraft:crafting_table', 1)
            craftingTable = [[int(b.x), int(b.y), int(b.z)] for b in craftingTable]
            craftingTable.sort(key=lambda b: Calc.distance(pos, b))
        
            if len(craftingTable) != 0:
                region = Region.createRegion(craftingTable[0], 3)
                Walk.walkTo(region)
                break    
            else:
                Craft.resetCraftingPlace()
                Logger.info('No crafting table found, building one')
                continue


    @staticmethod
    def openCraftingTable():
        """Open the crafting table"""
        Craft.goToCraftingTable()
        craftingTable =  World.findBlocksMatching('minecraft:crafting_table', 1)
        if len(craftingTable) == 0:
            raise CraftingError('No crafting table found')
        
        pos = Player.getPlayer().getPos()
        pos = [math.floor(pos.x), math.floor(pos.y), math.floor(pos.z)]
        
        craftingTable = [[math.floor(b.x), math.floor(b.y), math.floor(b.z)] for b in craftingTable]
        craftingTable.sort(key=lambda b: Calc.distance(pos, b))
        craftingTable = craftingTable[0]
        
        Action.interactBlock(craftingTable)
        Time.sleep(Craft.interactionDelay)


    @staticmethod
    def craftInHand(recipe: Recipe):
        """Craft the recipe in hand"""
        inventory = Player.openInventory()
        inventory.openGui()
        Time.sleep(Craft.interactionDelay)
        map = inventory.getMap()
        if 'crafting_in' not in map or 'craft_out' not in map:
            raise CraftingError('Not in a crafting table')
        
        if recipe.pattern is None: 
            for i, ingredient in enumerate(recipe.ingredients):
                id = ingredient.get('item', ingredient.get('tag', None))
                id = Dictionary.getGroup(id)
                # if id is None: continue
                itemSlot = Inv.getItem(id)
                slots = itemSlot['slots']
                slots = [s for s in slots if s not in map['crafting_in'] and s not in map['craft_out']]
                if len(slots) == 0:
                    raise CraftingError('Not enough items to craft ' + recipe.name)
                
                slot = slots[0]
                inventory.click(slot)
                inventory.click(map['crafting_in'][i], 1)
                inventory.click(slot)
                Time.sleep(Craft.interactionDelay)
                    
        else:
            for i, row in enumerate(recipe.pattern):
                for j, char in enumerate(row):
                    if char == ' ': continue
                    ingredient = recipe.key[char]
                    id = ingredient.get('item', ingredient.get('tag', None))
                    id = Dictionary.getGroup(id)
                    # if id is None: continue
                    itemSlot = Inv.getItem(id)
                    slots = itemSlot['slots']
                    slots = [s for s in slots if s not in map['crafting_in'] and s not in map['craft_out']]
                    if len(slots) == 0:
                        raise CraftingError('Not enough items to craft ' + recipe.name)
                    slot = slots[0]

                    inventory.click(slot)
                    inventory.click(map['crafting_in'][i*2+j], 1)
                    inventory.click(slot)
                    Time.sleep(Craft.interactionDelay)


        Time.sleep(Craft.interactionDelay)
        inventory.quick(map['craft_out'][0])
        Time.sleep(Craft.interactionDelay)
        inventory.close()
    

    @staticmethod
    def craftInTable(recipe: Recipe):
        """Craft the recipe in the crafting table"""
        Craft.openCraftingTable()
        Time.sleep(Craft.interactionDelay)
        inventory = Player.openInventory()
        map = inventory.getMap()

        if 'input' not in map or 'output' not in map:
            raise CraftingError('Not in a crafting table')        
        
        if recipe.pattern is None: 
            for i, ingredient in enumerate(recipe.ingredients):
                id = ingredient.get('item', ingredient.get('tag', None))
                id = Dictionary.getGroup(id)
                itemSlot = Inv.getItem(id)
                slots = itemSlot['slots']
                slots = [s for s in slots if s not in map['input'] and s not in map['output']]
                if len(slots) == 0:
                    raise CraftingError('Not enough items to craft ' + recipe.name)
                slot = slots[0]
                inventory.click(slot)
                inventory.click(map['input'][i], 1)
                inventory.click(slot)
                Time.sleep(Craft.interactionDelay)
            
        else:
            for i, row in enumerate(recipe.pattern):
                for j, char in enumerate(row):
                    if char == ' ': continue
                    ingredient = recipe.key[char]
                    id = ingredient.get('item', ingredient.get('tag', None))
                    id = Dictionary.getGroup(id)
                    itemSlot = Inv.getItem(id)
                    slots = itemSlot['slots']
                    slots = [s for s in slots if s not in map['input'] and s not in map['output']]
                    if len(slots) == 0:
                        raise CraftingError('Not enough items to craft ' + recipe.name)
                    
                    slot = slots[0]
                    shape = 2 if recipe.canCraftInHand() else 3

                    inventory.click(slot)
                    inventory.click(map['input'][i*shape+j], 1)
                    inventory.click(slot)
                    Time.sleep(Craft.interactionDelay)


        Time.sleep(Craft.interactionDelay)
        inventory.quick(map['output'][0])
        Time.sleep(Craft.interactionDelay)
        inventory.close()


    @staticmethod
    def craftInFurnace(recipe: Recipe):
        """Craft the recipe in the furnace"""
        raise NotImplementedError('Craft in furnace not implemented')


    @staticmethod
    def craft(*, recipe: Recipe = None, id: str = None, count: int = 1,
                listener: callable = lambda: None):
    
        """Craft the recipe"""
        # Implemention of GOAP algorithm
        if recipe is None and id is None:
            raise ValueError('recipe or id must be specified')
        
        elif recipe is None:
            ids = Dictionary.getIds(id)
            recipes = []
            for i in ids:
                recipes += Craft.getRecipes(i)
        else: 
            recipes = [recipe]

        if id is None:
            id = recipe.result['item']
            id = Dictionary.getGroup(id)

        Logger.info(f'Crafting {id} x{count}')

        if id in Craft.collectionMethods:
            func = Craft.collectionMethods[id]
            func(id, count)
            return

        if len(recipes) == 0:
            raise ValueError('No recipe found for id ' + id) 
        
        invItems = Inv.countItems()
        objective = count + invItems.get(id, 0)

        recipe = recipes[0] # TODO: select the best recipe and try all recipes if failed
        while True:
            listener()
            invItems = Inv.countItems()
            c = invItems.get(id, 0)
            # Logger.info(f'Crafting {id} x{count} ({c}/{objective})')
            if c >= objective: break

            recipeItems = recipe.countIngredients(count)
            recalc = False
            for _id in recipeItems:
                _id = Dictionary.getGroup(_id)
                if _id in invItems and invItems[_id] >= recipeItems[_id]: continue
                count_ = recipeItems[_id] - invItems.get(_id, 0)
                Craft.craft(id=_id, count=count_, listener=listener)
                recalc = True

            if recalc: continue

            if 'crafting' in recipe.type:
                if recipe.canCraftInHand():
                    Craft.craftInHand(recipe)
                else:
                    Craft.craftInTable(recipe)

            elif 'smelting' in recipe.type:
                Craft.craftInFurnace(recipe)

            else:
                raise NotImplementedError('Recipe type ' + recipe.type + ' not implemented yet')
