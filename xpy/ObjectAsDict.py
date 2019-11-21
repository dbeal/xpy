
try:
    from collections.abc import MutableMapping
except ImportError as e:
    from collections import MutableMapping

class ObjectAsDict(MutableMapping):
    #
    # use an object like a dict
    #
    def __init__(self, cls):
        self._obj = cls
    #
    def __delitem__(self, k):
        try:
            return delattr(self._obj, k)
        except AttributeError as e:
            raise KeyError(k)
            #
        #
    #
    def __getitem__(self, k):
        try:
            return getattr(self._obj, k)
        except AttributeError as e:
            raise KeyError(k)
            #
        #
    #
    def __setitem__(self, k, v):
        setattr(self._obj, k, v)
        #
    #
    def __iter__(self):
        return self._obj.__dict__.__iter__()
    #
    def __len__(self):
        return self._obj.__dict__.__len__()
        #
    #
#


