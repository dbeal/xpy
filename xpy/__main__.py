
import sys

from .Main import Main

class Foo(object):
    @classmethod
    def test(self):
        print('test')


def main():
    print('there')
    return Main.main()

if __name__ == '__main__':

    sys.exit(main())
