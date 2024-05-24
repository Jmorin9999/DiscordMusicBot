# commands/__init__.py
from bot.commands.betting import setup as betting_setup
from bot.commands.music import setup as music_setup
from bot.commands.user_management import setup as user_management_setup
from bot.commands.fun import setup as fun_setup
from bot.commands.roll import setup as roll_setup

__all__ = ['betting_setup', 'music_setup', 'user_management_setup', 'fun_setup','roll_setup']
