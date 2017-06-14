#!/usr/bin/env python3

import sys
import os

from .Clip import Clip

class XPY(object):
    @classmethod
    def setup_tab_completion(self):
        import rlcompleter
        import readline
        readline.parse_and_bind('tab: complete')

    def setup_history(self):
        from .RepoHistory import RepoHistory
        self.repo_history = RepoHistory('~/.pyhist')
        self.repo_history.clone()

    def commit_history(self):
        import readline
        self.repo_history.commit()

    def run(self):
        import code
        import readline

        self.setup_tab_completion()
        self.setup_history()

        ic = code.InteractiveConsole(globals())
        ic.interact()

        self.commit_history()

        return 33
