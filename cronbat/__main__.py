#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
import argparse
import inspect

from . import cli as controllers
from .colors import CRED, CEND

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# For every controller class defined in the commandline.controllers module we add a subparser
for _, cls in inspect.getmembers(controllers, inspect.isclass):
    # Only classes with _callable will be added as subparser (so to exclude utility classes)
    if getattr(cls, 'callable_cls', False):
        # Instantiate the controller class
        controller = cls()
        # Bind the subparser to the command defined in the class
        cls_parser = subparsers.add_parser(controller.command)
        cls_parser.set_defaults(func=controller._base)
        # Every method in the controller class will have it's own subparser
        method_parser = cls_parser.add_subparsers()
        for _, fnc in inspect.getmembers(controller, inspect.ismethod):
            if fnc.__name__ not in ('__init__', '_base'):
                method = method_parser.add_parser(fnc.__name__)
                # Bind the class method to the subparser argument
                method.set_defaults(func=fnc)

if __name__ == '__main__':
    args = parser.parse_args()
    try:
        args.func()
    except AttributeError:
        import traceback
        print(traceback.format_exc())
        print(f'{CRED}ERROR! Wrong command invocation, plese read the help:{CEND}')
        print(f'{CRED}Base usage:{CEND}')
        parser.print_help()
        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                print(f"\nCommand {CRED}'{choice}'{CEND}")
                print(subparser.format_help())
