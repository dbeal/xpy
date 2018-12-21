
#
# Copyright 2016-2018 David J. Beal, All Rights Reserved
#

# from xpy.Debug import Debug
from xpy.Anymethod import anymethod

_is_test_classes = False

class SuperMethod(object):
    """
    class MyClass(...):
        @SuperMethod
        def foo(super, self, *args, **kwargs):
            #
            # equivalent to super(MyClass, self).foo()
            #
            super.foo()
    #
    # A SuperMethod is provided with an appropriately populated super argument
    # which is equivalent to super(MyClass, self) for methods which do not have
    # access to a reference to *their own defining* class.
    #
    # This occurs in metaclasses which instantiate their own classes and
    # instances of the class which *itself* is in the process of being
    # constructed.  In that event, there is no reference to the class available
    # in the namespace of the function body.
    #

    """
    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    def __get__(self, obj, typ = None):

        # Debug.show_args()
        #
        pre = obj if obj is not None else typ

        cls = obj if isinstance(obj, type) else typ

        fn_name = getattr(self.fn, 'func_name', getattr(self.fn, '__name__'))

        for c in cls.__mro__:
            m = c.__dict__.get(fn_name)
            if m is not None:
                if m is self:
                    assert m is self
                    # found method
                    S = super(c, pre)
                    break
        else:
            S = None

        def _super(*args, **kwargs):
            return self(S, pre, *args, **kwargs)

        result = _super

        return result

if _is_test_classes:
    # SuperFoo.foo will only be invoked once between SuperBar and SuperCar
    #
    #######################
    #                     #
    #      SuperFoo       #
    #       /     \       #
    # SuperBar   SuperCar #
    #       \     /       #
    #      SuperBaz       #
    #          |          #
    #      SuperChaz      #
    #                     #
    #######################

    class SuperFoo(object):
        @anymethod
        def foo(self, x = None):
            print('SuperFoo', 'self', self, 'x', x)

    class SuperBar(SuperFoo):
        @SuperMethod
        def foo(super, self, x = None):
            super.foo('bar')
            print('SuperBar', 'self', self)

    class SuperCar(SuperFoo):
        @anymethod
        def foo(self, x = None):
            super(SuperCar, self).foo('car')
            print('SuperCar', 'self', self)

    class SuperBaz(SuperBar, SuperCar):
        @SuperMethod
        def foo(super, self, x = None):
            super.foo()
            # assert self is super.__self_class__
            # assert SuperBaz is super.__thisclass__
            print('SuperBaz', 'self', self)
            # print('bar', 'self', self)

    class SuperChaz(SuperBaz):
        pass

