# -*- coding: utf-8 -*-
from dag import DAG, ClientWrapper

def wrapper_test(**kwargs):
    print("{}".format(kwargs))
    return 1

client = ClientWrapper(wrapper_test)
dag = DAG([],client)
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
