""" Tests on the DAG implementation """

from nose import with_setup
from nose.tools import nottest, raises
from dag import DAG, DAGValidationError, Job, ClientWrapper

dag = None
jobs = [
    Job(jobName="a")
]

@nottest
def wrapper_test(**kwargs):
    return 1

@nottest
def blank_setup():
    global dag
    client = ClientWrapper(wrapper_test)
    dag = DAG(jobs, client)


@nottest
def start_with_graph():
    global dag
    client = ClientWrapper(wrapper_test)
    dag = DAG(jobs, client)
    dag.from_dict({'a': ['b', 'c'],
                   'b': ['d'],
                   'c': ['d'],
                   'd': []})


@with_setup(blank_setup)
def test_add_node():
    dag.add_node('a')
    assert dag.graph == {'a': set()}


@with_setup(blank_setup)
def test_add_edge():
    dag.add_node('a')
    dag.add_node('b')
    dag.add_edge('a', 'b')
    assert dag.graph == {'a': set('b'), 'b': set()}


@with_setup(blank_setup)
def test_from_dict():
    dag.from_dict({'a': ['b', 'c'],
                   'b': ['d'],
                   'c': ['d'],
                   'd': []})
    assert dag.graph == {'a': set(['b', 'c']),
                         'b': set('d'),
                         'c': set('d'),
                         'd': set()}


@with_setup(blank_setup)
def test_reset_graph():
    dag.add_node('a')
    assert dag.graph == {'a': set()}
    dag.reset_graph()
    assert dag.graph == {}


@with_setup(start_with_graph)
def test_ind_nodes():
    inodes = dag.ind_nodes(dag.graph)
    print(inodes)
    assert inodes == ['a']


@with_setup(blank_setup)
def test_topological_sort():
    dag.from_dict({'a': [],
                   'b': ['a'],
                   'c': ['b']})
    assert dag.topological_sort() == ['c', 'b', 'a']


@with_setup(start_with_graph)
def test_successful_validation():
    assert dag.validate()[0] == True


@raises(DAGValidationError)
@with_setup(blank_setup)
def test_failed_validation():
    dag.from_dict({'a': ['b'],
                   'b': ['a']})


@with_setup(start_with_graph)
def test_downstream():
    assert set(dag.downstream('a', dag.graph)) == set(['b', 'c'])


@with_setup(start_with_graph)
def test_all_downstreams():
    assert dag.all_downstreams('a') == ['c', 'b', 'd']
    assert dag.all_downstreams('b') == ['d']
    assert dag.all_downstreams('d') == []


@with_setup(start_with_graph)
def test_all_downstreams_pass_graph():
    client = ClientWrapper(wrapper_test)
    dag2 = DAG(jobs, client)
    dag2.from_dict({'a': ['c'],
                    'b': ['d'],
                    'c': ['d'],
                    'd': []})
    assert dag.all_downstreams('a', dag2.graph) == ['c', 'd']
    assert dag.all_downstreams('b', dag2.graph) == ['d']
    assert dag.all_downstreams('d', dag2.graph) == []


@with_setup(start_with_graph)
def test_predecessors():
    assert set(dag.predecessors('a')) == set([])
    assert set(dag.predecessors('b')) == set(['a'])
    assert set(dag.predecessors('c')) == set(['a'])
    assert set(dag.predecessors('d')) == set(['b', 'c'])


@with_setup(start_with_graph)
def test_all_leaves():
    assert dag.all_leaves() == ['d']


@with_setup(start_with_graph)
def test_size():
    assert dag.size() == 4
    dag.delete_node('a')
    assert dag.size() == 3

@with_setup(start_with_graph)
def test_run_jobs():
    assert len(dag.jobs) == 1
    dag.run()
    assert jobs[0].id == 1
