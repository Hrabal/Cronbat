# -*- coding: utf-8 -*-
"""
Collection of all the command line controllers we're gonna provide to the command line API
"""
from .cronbat import Cron


class CommanlineController:
    def __init__(self):
        self.cron = Cron()

    def _base(self):
        raise NotImplemented


class MinusL(CommanlineController):
    callable_cls = True
    command = 'l'

    def _base(self):
        print(self.cron.dump_cron(to_cron=False))

    def init(self):
        print('init!')


class MinusR(CommanlineController):
    callable_cls = True
    command = 'r'

    def _base(self):
        self.cron._r()
