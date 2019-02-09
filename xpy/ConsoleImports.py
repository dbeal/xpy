#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

class ConsoleImports(object):
    """
    For convenience, names bound within this class will be linked to the
    globals of the interpreter.
    """
    from .Clip import Clip
    # from .Plot import Plot
    from .Colors import Colors
    from .Micros import Micros as M
    from .XPY import ResumEx, rese
    from .Profiler import Profiler
    from .Builtins import EA, FL, ls
    from .Debug import Debug
    from .History import History

