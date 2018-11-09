# -*- coding: utf-8 -*-
"""
Collection of all the command line controllers we're gonna provide to the command line API
"""
from cronbat import Cron


class CommanlineController:
    def __init__(self):
        self.cron = Cron()

    def _base(self):
        raise NotImplemented


class MinusL(CommanlineController):
    """With no extra params is equivalent to 'contab -l', lists the current crontab"""
    callable_cls = True
    command = 'l'

    def _base(self):
        print(self.cron.dump_cron(to_cron=False, pretty=True))

    def section(self, section_name: str):
        """Filters the listing to the specified section."""
        section_name = section_name or 'main'
        print(self.cron.dump_cron(to_cron=False, pretty=True, section=section_name))


class MinusR(CommanlineController):
    """Equivalent to 'contab -r', erease the crontab."""
    callable_cls = True
    command = 'r'

    def _base(self):
        self.cron._r()


class MinusE(CommanlineController):
    """Equivalent to 'contab -e', edit crontab entries with configured editor."""
    callable_cls = True
    command = 'e'

    def _base(self):
        self.cron.edit_section(['main', ])
        self.cron.dump_cron()

    def section(self, section_name: str):
        """Filters the listing to the specified section."""
        section_name = section_name or 'main'
        print(self.cron.edit_section(to_cron=False, pretty=True, section=section_name))
