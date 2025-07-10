from __future__ import annotations
from typing import Iterator
import math
from itertools import product

if __name__ == '':
    from JsMacrosAC import *
    

class Region:
    """A class for representing a rectangular region in n-dimensional space"""

    def __init__(self, pos1: list[int], pos2: list[int]):
        self.minPos = []
        for i in range(len(pos1)):
            self.minPos.append(min(pos1[i], pos2[i]))

        self.maxPos = []
        for i in range(len(pos1)):
            self.maxPos.append(max(pos1[i], pos2[i]))

    def contains(self, pos: list[int]) -> bool:
        """Check if a position is inside the region"""
        for i in range(len(pos)):
            if pos[i] < self.minPos[i] or pos[i] > self.maxPos[i]:
                return False
        
        return True

    def getCenter(self) -> list[int]:
        """Get the center of the region"""
        return [(self.minPos[i] + self.maxPos[i]) / 2 for i in range(len(self.minPos))]

    def getBounds(self) -> list[list[int]]:
        """Get the bounds of the region"""
        return [self.minPos, self.maxPos]

    def getDimension(self) -> int:
        """Get the dimension of the region"""
        return len(self.minPos)

    def getSize(self) -> list[int]:
        """Get the size of the region"""
        return [self.maxPos[i] - self.minPos[i] for i in range(len(self.minPos))]
    
    def copy(self) -> Region:
        """Return a copy of the region"""
        return Region(self.minPos, self.maxPos)
    
    def intersection(self, region: Region) -> Region:
        """Return the intersection of two regions"""
        minPos = []
        maxPos = []

        for i in range(len(self.minPos)):
            minPos.append(max(self.minPos[i], region.minPos[i]))
            maxPos.append(min(self.maxPos[i], region.maxPos[i]))

        return Region(minPos, maxPos)

    def iterate(self) -> Iterator[list[int]]:
        """Iterate over all the positions in the region"""
        ranges = [range(math.floor(self.minPos[i]), math.floor(self.maxPos[i]) + 1) for i in range(len(self.minPos))]

        for pos in product(*ranges):
            yield list(pos)

    def divide(self, cellSize: list[int]) -> Iterator[Region]:
        """Divide the region into cells of a given size"""
        assert len(cellSize) == len(self.minPos), "The cell size must have the same dimensions as the region"

        ranges = [range(math.floor(self.minPos[i]), math.floor(self.maxPos[i]), cellSize[i]) for i in range(len(self.minPos))]

        for pos in product(*ranges):
            pos1 = pos
            pos2 = [pos[i] + cellSize[i] for i in range(len(pos))]

            yield Region(pos1, pos2)


    @staticmethod
    def createRegion(pos: list[int], size: int | list[int]) -> Region:
        """Create a region from a given position as the center and a size"""
        if not isinstance(size, list):
            size = [size for i in range(len(pos))]

        assert len(pos) == len(size), "The position and size must have the same dimensions"

        pos1 = []
        for i in range(len(pos)):
            pos1.append(pos[i] - size[i] / 2)

        pos2 = []
        for i in range(len(pos)):
            pos2.append(pos[i] + size[i] / 2)

        return Region(pos1, pos2)


class Calc:
    """A class for calculating things"""
    @staticmethod
    def distance(point1: list[int], point2: list[int]) -> float:
        """Calculate the distance between two points in n-dimensional space"""

        assert len(point1) == len(point2), "Points must have the same dimensions to calculate distance"

        return sum([(point1[i] - point2[i]) ** 2 for i in range(len(point1))]) ** 0.5
    

    @staticmethod
    def pointOnLine(start: list[int], end: list[int], distance: float) -> list[int]:
        """Calculate a point on a line between two points at 
        a given distance from the start point"""

        angle = math.atan2(end[0] - start[0], end[2] - start[2])
        x = start[0] + math.sin(angle) * distance
        z = start[2] + math.cos(angle) * distance

        # y is not necessary for this function,
        # normally it will be calculated from the terrain
        # for example, searching for the ground level at a given x and z
        y = start[1]

        return [x, y, z]


    @staticmethod
    def binarySearchIndex(array: list, value: any) -> int:
        """Search for a value in a sorted array and return the index of the value.
        If the value is not in the array, return the index where it should be inserted"""
        low = 0
        high = len(array) - 1

        while low <= high:
            mid = (low + high) // 2

            if array[mid] < value:
                low = mid + 1
            elif array[mid] > value:
                high = mid - 1
            else:
                return mid

        return low

