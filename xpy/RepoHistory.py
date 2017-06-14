#!/usr/bin/env python

# History file is merged using git to keep all appends from multiple sources.

import tempfile
import os
import numba

from six.moves import map
from itertools import *
from cytoolz.curried import *
import readline

import sys

def streamer(fd, chunk):
    while True:
        buf = os.read(fd, chunk)
        if buf:
            yield buf
        else:
            break

def groupcomplete(it, is_completion):
    """is_completion returns true for the element that indicates a complete set"""
    p = None
    for e in it:
        if is_completion(e):
            if p is not None:
                yield p + [e]
                p = None
            else:
                yield [e]
        else:
            if p is not None:
                p.append(e)
            else:
                p = [e]
    if p is not None:
        yield p

def splitter(bufs, eol):
    return map(eol[:0].join, groupcomplete(concat(bufs), lambda e: e == eol))

class RepoHistory(object):
    def __init__(self, repo_url):
        self.tmpdir = tempfile.mkdtemp(prefix = 'hist.')
        self.repo_url = os.path.expanduser(repo_url)
        self.clone_path = os.path.join(self.tmpdir, os.path.basename(self.repo_url))
        self.history_path = '.pyhistory'
        self.history_abspath = os.path.join(self.clone_path, self.history_path)
        self.attributes_file_path = os.path.join(self.clone_path, '.git/info/attributes')
        self.master_pid = os.getpid()

        self.clone()

    def clone(self):
        if not os.path.exists(self.repo_url):
            os.system('git init --bare {repo_url}'.format(**self.__dict__))

        os.system('git clone {repo_url} {clone_path}'.format(**self.__dict__))

        if os.path.exists(self.history_abspath):
            readline.read_history_file('{history_abspath}'.format(**self.__dict__))

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
            for line in splitter(streamer(fd, 3), eol):
                if line == attr_line:
                    break
                    is_attr_present = True
            if not is_attr_present:
                os.write(fd, attr_line.encode())
        finally:
            os.close(fd)

    def commit(self):
        if os.getpid() == self.master_pid:
            od = os.getcwd()
            os.chdir(self.clone_path)
            self.set_attribute(self.attributes_file_path, self.history_path, ['merge=union'])
            # fd = os.open(self.attributes_file_path, os.O_RDONLY)
            # os.close(fd)
            print('sys.meta_path', sys.meta_path)
            return
            print('importing readling')
            readline.write_history_file(self.history_abspath)
            print('done importing readling')
            os.system('git add {history_path} && git commit -mwip ; git fetch && {{ [ -e ".git/refs/remotes/origin/HEAD" ] && git merge -munion || echo new master; }} && echo git push'.format(**self.__dict__))
            os.chdir(od)
            os.system('rm -rf {tmpdir}'.format(**self.__dict__))
        else:
            # print('not the master process--not committing')
            pass
        pass

