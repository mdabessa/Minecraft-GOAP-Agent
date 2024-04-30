from __future__ import annotations
import json
import os


if __name__ == '':
    from JsMacrosAC import *
    from libs.utils.logger import Logger, Style

saves = os.path.join(os.getcwd(), 'config', 'jsMacros', 'Macros', 'states')


class State:
    """Class to manage the state of the agent."""
    def __init__(self, name: str = None, path: str = None):
        name = name if name is not None else self.genName()
        name = f'{name}.json' if not name.endswith('.json') else name
        self.name = name
        
        self.path = path if path is not None else os.path.join(saves, self.name)
        self.state = {}
        
        self.load()


    def genName(self) -> str:
        """Function to generate a name for the state."""
        name = World.getWorldIdentifier()
        return name


    def load(self):
        """Function to load the state from the file."""
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.state = json.load(f)

    def save(self):
        """Function to save the state to the file."""
        with open(self.path, 'w') as f:
            json.dump(self.state, f, indent=4)


    def get(self, key: str, default = None):
        """Function to get a value from the state."""
        return self.state.get(key, default)


    def set(self, key: str, value):
        """Function to set a value in the state."""
        self.state[key] = value


    def __getitem__(self, key: str):
        """Function to get an item from the state."""
        return self.state[key]


    def __setitem__(self, key: str, value):
        """Function to set an item in the state."""
        self.state[key] = value


class Waypoint:
    """Class to represent a waypoint."""
    def __init__(self, name: str, x: int, y: int, z: int, dimension: str, state: State = None):
        if state is None:
            state = State()
        
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.dimension = dimension
        self.state = state

    def save(self):
        """Function to save the waypoint to the state."""
        wps = self.state.get('waypoints', {})
        wps[self.name] = {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'dimension': self.dimension
        }

        self.state['waypoints'] = wps
        self.state.save()

    def delete(self):
        """Function to delete the waypoint from the state."""
        wps = self.state.get('waypoints', {})
        if self.name in wps:
            del wps[self.name]

        self.state['waypoints'] = wps
        self.state.save()

    def __str__(self) -> str:
        """Function to get the string representation of the waypoint."""
        return f'Waypoint(name={self.name}, x={self.x}, y={self.y}, z={self.z}, dimension={self.dimension})'

    @staticmethod
    def getWaypoints(state: State = None) -> list[Waypoint]:
        """Function to get all the waypoints from the state."""
        if state is None:
            state = State()

        wps = state.get('waypoints', {})
        waypoints = {}
        for name, wp in wps.items():
            waypoints[name] = Waypoint(name, wp['x'], wp['y'], wp['z'], wp['dimension'], state)
        
        return waypoints

    @staticmethod
    def getWaypoint(name: str, state: State = None) -> Waypoint | None:
        """Function to get a waypoint from the state."""
        if state is None:
            state = State()

        waypoints = Waypoint.getWaypoints(state)    
        return waypoints.get(name, None)
    
    @staticmethod
    def addWaypoint(name: str, x: int, y: int, z: int, dimension: str, state: State = None) -> Waypoint:
        """Function to add a waypoint to the state."""
        if state is None:
            state = State()

        waypoint = Waypoint(name, x, y, z, dimension, state)
        waypoint.save()
        return waypoint

    @staticmethod
    def delWaypoint(name: str, state: State = None):
        """Function to delete a waypoint from the state."""
        if state is None:
            state = State()

        waypoint = Waypoint.getWaypoint(name, state)
        if waypoint is not None:
            waypoint.delete()
