#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import sys

from .Colors import Colors

class anymethod(object):
    def __new__(cls, fn):
        self = object.__new__(cls)
        self.fn = fn
        return self

    def __call__(self, *args, **kwargs):
        """Static function invoke like fn(self, *args, **kwargs)"""
        return self.fn(*args, **kwargs)

    def __get__(self, obj = None, typ = None):
        """
        # If the second argument is not None, pass it as the first argument
        # in the bound function.
        #
        # Otherwise, if the third argument is not None, pass it as the
        # first argument.
        #
        # Otherwise, pass None as the first argument in the bound function.
        # usage:

        @anymethod
        def fn(self, *args, **kwargs):
            # self is any of:
            # 1. instance (instance method)
            # 2. class (classmethod)
            # 3. None (staticmethod)
            pass

        """

        # TODO: optimize this, as it's still somewhat slower than @classmethod,
        # @staticmethod, etc.
        # types.FunctionType and curry seem slower

        pre = obj if obj is not None else typ

        if 1:
            def _anymethod(*args, **kwargs):
                # lookup fn each invoke
                # fn can be changed
                return self(pre, *args, **kwargs)
        else:
            fn = self.fn

            def _anymethod(*args, **kwargs):
                # lookup fn once
                return fn(pre, *args, **kwargs)

        return _anymethod

