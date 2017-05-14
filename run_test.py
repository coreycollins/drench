# -*- coding: utf-8 -*-
from dag import DAG
dag = DAG()
dag.from_dict({'a': ['b', 'c'],
               'b': ['d'],
               'c': ['d'],
               'd': []})

val = dag.all_downstreams('a')
print(val)