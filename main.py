from libs.importer import require, LIBS
import time
import math

require('__all__', globals())

if __name__ == "":
    from JsMacrosAC import *
    from libs.utils.calc import Calc, Region
    from libs.walk import Walk, Node, Block
    from libs.scripts import Script
    from libs.gathering.wood import Wood
    from libs.inventory import Inv
    from libs.explorer import Explorer
    from libs.actions import Action
    from libs.craft import Craft
    from libs.test import Test, getEnvironment


Chat.log("Hello World!")
