# -*- coding: utf-8 -*-
from dag import DAG

dag = DAG()
dag.from_dict(
    {'a': ['b', 'c'],
     'b': ['d'],
     'c': ['d'],
     'd': [],
     'e': ['d']
     }
)

val = dag.all_downstreams('a')

ind_node = dag.ind_nodes()
print(ind_node)
