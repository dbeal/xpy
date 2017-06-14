#!/usr/bin/env python3

import sys
import os

from .Clip import Clip
from .Plot import Plot

class XPY(object):
    @classmethod
    def setup_tab_completion(self, namespace):
        import rlcompleter
        import readline
        completer = rlcompleter.Completer(namespace)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

    def setup_history(self):
        from .RepoHistory import RepoHistory
        self.repo_history = RepoHistory('~/.pyhist')
        self.repo_history.clone()

    def commit_history(self):
        self.repo_history.commit()

    def run(self, namespace):
        import code

        self.setup_tab_completion(namespace)
        self.setup_history()

        ic = code.InteractiveConsole(namespace)
        ic.interact()

        self.commit_history()

        return 33

