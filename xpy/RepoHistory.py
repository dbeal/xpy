#!/usr/bin/env python
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

#
# History file is merged using git to keep all appends from multiple sources.
#

import tempfile
import os

from six.moves import map
# from itertools import *
# from cytoolz.curried import *
import readline

import sys

from .Text import Text
from .File import File

class RepoHistory(object):
    def __init__(self, repo_url):
        self.tmpdir = tempfile.mkdtemp(prefix = 'hist.')
        self.repo_url = os.path.expanduser(repo_url)
        self.clone_path = os.path.join(self.tmpdir, os.path.basename(self.repo_url))
        self.history_path = '.pyhistory'
        self.history_abspath = os.path.join(self.clone_path, self.history_path)
        self.attributes_file_path = os.path.join(self.clone_path, '.git/info/attributes')
        self.master_pid = os.getpid()

    def clone(self):
        if not os.path.exists(self.repo_url):
            os.system(' '.join(['git init --bare ', self.repo_url]))

        os.system(' '.join(['git clone ', self.repo_url, ' ', self.clone_path]))

        self.read_history()

    def read_history(self):
        if os.path.exists(self.history_abspath):
            readline.clear_history()
            readline.read_history_file(self.history_abspath)
            #
            # print(' '.join(['read history file', self.history_abspath]))
            #

    # set a git attribute
    def set_attribute(self, attributes_file_path, path, attrs):
        # change merge driver to "union" for history files which tend to be
        # append-only from multiple sources.

        eol = '\n'

        # write the following line to .git/info/attributes file if it isn't
        # already there.
        # .pyhistory merge=union
        attr_line = ' '.join([path] + attrs) + eol

        is_attr_present = False
        fd = os.open(attributes_file_path, os.O_RDWR | os.O_CREAT)
        try:
            for line in Text.splitter(File.streamer(fd, 3), eol):
                if line == attr_line:
                    break
                    is_attr_present = True
            if not is_attr_present:
                os.write(fd, attr_line.encode())
        finally:
            os.close(fd)

    def write_history(self):
        readline.write_history_file(self.history_abspath)
        #
        # print(' '.join(['wrote history file', self.history_abspath]))
        #

    def commit(self):
        if os.getpid() == self.master_pid:
            self.write_history()

            od = os.getcwd()
            os.chdir(self.clone_path)

            # update merge attribute
            self.set_attribute(self.attributes_file_path, self.history_path, ['merge=union'])

            os.system(' '.join(['git diff -b && git add ', self.history_path, ' && git commit -mwip ; git fetch && { [ -e ".git/refs/remotes/origin/HEAD" ] && git merge -munion || echo new master; } && git push']))
            os.chdir(od)
            #
            print(' '.join(['removing', self.tmpdir]))
            #
            assert os.path.exists(self.tmpdir)
            #
            status = os.system(' '.join(['rm', '-rf', "'" + self.tmpdir + "'"]))
            #
        else:
            #
            print('not the master process--not committing')
            #
            pass
        pass

