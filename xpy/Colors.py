#!/usr/bin/env python3

#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

import os

class Colors(object):
    ESC = '\x1b'
    S = ESC + '['

    GREY = S + "1;30m"
    RED = S + "1;31m"
    GREEN = S + "1;32m"
    YELLOW = S + "1;33m"
    BLUE = S + "1;34m"
    MAGENTA = S + "1;35m"
    CYAN = S + "1;36m"
    WHITE = S + "1;37m"

    BGGREY = S + "1;40m"
    BGRED = S + "1;41m"
    BGGREEN = S + "1;42m"
    BGYELLOW = S + "1;43m"
    BGBLUE = S + "1;44m"
    BGMAGENTA = S + "1;45m"
    BGCYAN = S + "1;46m"
    BGWHITE = S + "1;47m"

    NORM = S + "m"

    #
    # readline metrics for computing length of prompt without counting the
    # bytes used for ansi codes
    #
    # RL_PROMPT_START_IGNORE
    RLPSI = '\001'
    # RL_PROMPT_END_IGNORE
    RLPEI = '\002'

    RLGREY = RLPSI + GREY + RLPEI
    RLRED = RLPSI + RED + RLPEI
    RLGREEN = RLPSI + GREEN + RLPEI
    RLYELLOW = RLPSI + YELLOW + RLPEI
    RLBLUE = RLPSI + BLUE + RLPEI
    RLMAGENTA = RLPSI + MAGENTA + RLPEI
    RLCYAN = RLPSI + CYAN + RLPEI
    RLWHITE = RLPSI + WHITE + RLPEI

    RLBGGREY = RLPSI + BGGREY + RLPEI
    RLBGRED = RLPSI + BGRED + RLPEI
    RLBGGREEN = RLPSI + BGGREEN + RLPEI
    RLBGYELLOW = RLPSI + BGYELLOW + RLPEI
    RLBGBLUE = RLPSI + BGBLUE + RLPEI
    RLBGMAGENTA = RLPSI + BGMAGENTA + RLPEI
    RLBGCYAN = RLPSI + BGCYAN + RLPEI
    RLBGWHITE = RLPSI + BGWHITE + RLPEI

    RLNORM = RLPSI + NORM + RLPEI

class ANSI(object):
    @classmethod
    def HOME(self, R, C):
        return self.S + str(R) + ';' + str(C) + 'H'

# Don't use these escape codes
# TODO: just use functions
if not (os.isatty(1) and os.isatty(2)):
    for k in Colors.__dict__:
        v = getattr(Colors, k)
        if type(v) is str and v[0] == v[0].upper():
            setattr(Colors, k, '')

