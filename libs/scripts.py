import json
import time

if __name__ == '': from JsMacrosAC import *


class ScriptStoppedError(Exception):
    """Exception to stop a script."""
    pass

class ScriptNameAlreadyExistsError(Exception):
    """Exception to script name already exists."""
    pass


class Script: 
    @staticmethod
    def getScripts() -> dict:
        """Function to get all scripts registered in the global controller."""
        scripts = GlobalVars.getString('scripts')
        if scripts == None: return {}
        scripts = json.loads(scripts)
        return scripts

    @staticmethod
    def setScripts(scripts: dict):
        """Function to set all scripts registered in the global controller."""

        scripts = json.dumps(scripts)
        GlobalVars.putString('scripts', scripts)

    @staticmethod
    def addScript(name: str):
        """Function to register a script in the global controller."""
        script = {
            'name': name,
            'created': time.time(),
        }
        scripts = Script.getScripts()

        if name in scripts:
            raise ScriptNameAlreadyExistsError(f'Script name [{name}] already exists.')

        scripts[name] = script
        Script.setScripts(scripts)


    @staticmethod
    def getScript(name: str) -> dict | None:
        """Function to get a script registered in the global controller."""
        scripts = Script.getScripts()
        if name in scripts:
            return scripts[name]
        return None


    @staticmethod
    def removeScript(name: str):
        """Function to remove a script registered in the global controller."""
        scripts = Script.getScripts()
        if name in scripts:
            del scripts[name]
        
        Script.setScripts(scripts)

    @staticmethod
    def scriptListener(name: str):
        """Create a function to kill a script if not registered or removed in the global controller."""
        Script.addScript(name)
        def func():
            script = Script.getScript(name)
            if script == None:
                raise ScriptStoppedError('Script not registered or removed.')

        return func
    

    @staticmethod
    def stopScript(name: str):
        """Function to stop a script registered in the global controller."""
        scripts = Script.getScripts()
        if name in scripts:
            del scripts[name]
            Script.setScripts(scripts)


    @staticmethod
    def stopAllScripts():
        """Function to stop all scripts registered in the global controller."""
        Script.setScripts({})


    @staticmethod
    def stopAllScriptsExcept(name: str):
        """Function to stop all scripts registered in the global controller except one."""
        scripts = Script.getScripts()
        if name in scripts:
            Script.setScripts({name: scripts[name]})
        else:
            Script.setScripts({})
