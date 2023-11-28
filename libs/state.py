from __future__ import annotations
import json
import os


if __name__ == '':
    from JsMacrosAC import *

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
