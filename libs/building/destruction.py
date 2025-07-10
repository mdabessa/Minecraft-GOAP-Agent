import math

if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.utils.dictionary import Dictionary
    from libs.utils.logger import Logger
    from libs.scripts import Script
    from libs.walk import Walk, Block
    from libs.actions import Action
    from libs.state import State, Waypoint
    from libs.inventory import Inv
    from libs.craft import Craft
    from libs.explorer import Explorer



class Destruction:
    @staticmethod
    def destroy(region: Region, cellSize: list = None):
        listener = Script.scriptListener('Destruction')
        
        Logger.info(f"Destroying region {region.minPos} to {region.maxPos}")
        if cellSize is None:
            cellSize = [2, 2, 2]

        cells = list(region.divide(cellSize))

        i = 1
        total = len(cells)
        while len(cells) > 0:
            listener()

            player = Player.getPlayer()
            playerPos = player.getPos()
            playerPos = [playerPos.x, playerPos.y, playerPos.z]

            cells.sort(key=lambda cell: (cell.minPos[1], -Calc.distance(cell.getCenter(), playerPos)), reverse=True)
            cell = cells[0]

            if Destruction.checkIfCellIsEmpty(cell):
                Logger.debug(f"Cell {cell.minPos} to {cell.maxPos} is empty!")
                cells.remove(cell)
                i += 1
                continue

            Logger.info(f"Destroying cell {cell.minPos} to {cell.maxPos} ({i}/{total})")
            Walk.walkTo(cell)
            Action.breakAllBlocks(region=cell, safe=False)

        Script.stopScript('Destruction')
        Logger.info("Finished destroying region")

    @staticmethod
    def checkIfCellIsEmpty(region: Region):
        for pos in region.iterate():
            block = Block.getBlock(pos)
            if block.isSolid:
                return False

        return True
