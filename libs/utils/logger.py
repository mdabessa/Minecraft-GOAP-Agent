from __future__ import annotations
import os
import datetime

if __name__ == '':
    from JsMacrosAC import *


class Style:
    """Enum for color codes"""
    DARK_RED = '&4'
    RED = '&c'
    GOLD = '&6'
    YELLOW = '&e'
    DARK_GREEN = '&2'
    GREEN = '&a'
    AQUA = '&b'
    DARK_AQUA = '&3'
    DARK_BLUE = '&1'
    BLUE = '&9'
    LIGHT_PURPLE = '&d'
    DARK_PURPLE = '&5'
    WHITE = '&f'
    GRAY = '&7'
    DARK_GRAY = '&8'
    BLACK = '&0'
    OBFUSCATED = '&k'
    BOLD = '&l'
    STRIKETHROUGH = '&m'
    UNDERLINE = '&n'
    ITALIC = '&o'
    RESET = '&r'


class LoggerLevel:
    """Enum for logger levels"""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger:
    """Logger class to log messages to the game"""
    level = LoggerLevel.INFO
    logPath = './config/jsMacros/Macros/logs/latest.log'

    @staticmethod
    def printStyles() -> None:
        """Prints all styles"""
        for key, value in Style.__dict__.items():
            if not key.startswith('__') and not callable(value):
                Chat.logColor(f'{value}{key}')

    @staticmethod
    def print(message: str) -> None:
        """Prints a message to the game"""
        message = str(message)
        Chat.logColor(message)

    @classmethod
    def debug(cls, message: str) -> None:
        """Prints a debug message to the game"""
        if cls.level <= LoggerLevel.DEBUG:
            cls.print(f'{Style.WHITE}[{Style.DARK_GRAY}DEBUG{Style.WHITE}] {message}')
        
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        Logger.save(f'{date} [DEBUG] {message}')

    @classmethod
    def info(cls, message: str) -> None:
        """Prints an info message to the game"""
        if cls.level <= LoggerLevel.INFO:
            cls.print(f'{Style.WHITE}[{Style.GRAY}INFO{Style.WHITE}] {message}')

        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        Logger.save(f'{date} [INFO] {message}')

    @classmethod
    def warning(cls, message: str) -> None:
        """Prints a warning message to the game"""
        if cls.level <= LoggerLevel.WARNING:
            cls.print(f'{Style.WHITE}[{Style.YELLOW}WARNING{Style.WHITE}] {message}')
        
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        Logger.save(f'{date} [WARNING] {message}')
        
    @classmethod
    def error(cls, message: str) -> None:
        """Prints an error message to the game"""
        if cls.level <= LoggerLevel.ERROR:
            cls.print(f'{Style.WHITE}[{Style.DARK_RED}ERROR{Style.WHITE}] {message}')
        
        date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        Logger.save(f'{date} [ERROR] {message}')

    @classmethod
    def save(cls, message: str) -> None:
        """Saves a message to the log file"""
        # return # Disable logging to file
        path = os.path.dirname(cls.logPath)
        if not os.path.exists(path):
            os.makedirs(path)

        with open(cls.logPath, 'a', encoding='utf-8') as file:
            file.write(f'{message}\n')
