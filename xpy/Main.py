#!/usr/bin/env python3

class Main(object):
    @classmethod
    def main(self):
        from .XPY import XPY
        xpy = XPY()
        return xpy.run()

if __name__ == '__main__':
    import sys
    sys.exit(Main.main())
