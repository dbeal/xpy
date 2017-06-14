#!/usr/bin/env python3

import code
import readline
import sys

from .Clip import Clip

class XPY(object):
    pass
    def __init__(self):
        self.setup_history()

    @classmethod
    def setup_tab_completion(self):
        import rlcompleter, readline
        readline.parse_and_bind('tab: complete')

    @classmethod
    def setup_history(self):
        import rlcompleter, readline
        self.startup_history_length = readline.get_current_history_length()

    def run(self):
        ic = code.InteractiveConsole()
        ic.interact()
        return 33

    def __del__(self):
        print(('xpy dtor'))

