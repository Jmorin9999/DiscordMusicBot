# commands/__init__.py
from .betting import setup as betting_setup
from .music import setup as music_setup
from .user_management import setup as user_management_setup
from .fun import setup as fun_setup

__all__ = ['betting_setup', 'music_setup', 'user_management_setup', 'fun_setup']
