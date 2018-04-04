"""taxonomy!"""
from collections.abc import Mapping

class Taxonomy(Mapping):
    """file layout"""
    def __init__(self, *args, **kw):
        self._storage = dict(*args, **kw)
    def __getitem__(self, key):
        return self._storage[key]
    def __iter__(self):
        return iter(self._storage)
    def __len__(self):
        return len(self._storage)
    def __str__(self):
        return dict(self).__str__()

    def to_json(self):
        '''make json.dumps-friendly dict'''
        out_dict = {}
        for key, val in self._storage.items():
            out_dict[key] = val.__name__
        return out_dict
