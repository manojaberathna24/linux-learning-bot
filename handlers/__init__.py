"""Handlers package initialization"""
from handlers.start import setup_start_handlers
from handlers.settings import setup_settings_handlers
from handlers.admin import setup_admin_handlers
from handlers.terminal import setup_terminal_handlers
from handlers.learn import setup_learn_handlers
from handlers.ask import setup_ask_handlers
from handlers.labsheet import setup_labsheet_handlers
from handlers.quiz import setup_quiz_handlers
from handlers.cheatsheet import setup_cheatsheet_handlers

__all__ = [
    'setup_start_handlers',
    'setup_settings_handlers',
    'setup_admin_handlers',
    'setup_terminal_handlers',
    'setup_learn_handlers',
    'setup_ask_handlers',
    'setup_labsheet_handlers',
    'setup_quiz_handlers',
    'setup_cheatsheet_handlers',
]
