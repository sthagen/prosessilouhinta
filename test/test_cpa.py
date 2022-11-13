import json
import operator
import pathlib

import prosessilouhinta.cpa as cpa

CPA_MICRO_FIXTURE_PATH = pathlib.Path('test', 'fixtures', 'basic', 'cpa-micro.json')
CPA_SMALL_FIXTURE_PATH = pathlib.Path('test', 'fixtures', 'basic', 'cpa-small.json')
CPA_SMALL_FIXTURE_CRITICAL_PATH = pathlib.Path('test', 'fixtures', 'basic', 'cpa-small-critical-path-nodes.json')

with open(CPA_SMALL_FIXTURE_CRITICAL_PATH, 'rt', encoding='utf-8') as handle:
    CPA_SMALL_CRTICAL_PATH_EXPECTED = json.load(handle)


def test_cpa_cyclic_empty_dgraph():
    empty = {}
    assert cpa.cyclic(empty) is False


def test_cpa_cyclic_on_minimal_cyclic_dgraph():
    good = {'a': ('a',)}
    assert cpa.cyclic(good) is True


def test_cpa_cyclic_on_acyclic_dgraph():
    good = {'a': ('z',), 'z': ('b',), 'b': ('y', 'c')}
    assert cpa.cyclic(good) is False


def test_cpa_cyclic_on_cyclic_dgraph():
    bad = {'a': ('z',), 'z': ('b',), 'b': ('y', 'z')}
    assert cpa.cyclic(bad) is True


def test_cpa_nodes():
    nodes = set()
    n1 = cpa.Node(name=1, duration=1)
    n2 = cpa.Node(name=2, duration=1)
    n2a = cpa.Node(name=2, duration=1)
    assert n2 == n2a
    nodes.add(n1)
    nodes.add(n2)
    nodes.add(n2a)
    assert len(nodes) == 2

    parent = cpa.Node('parent')
    assert len(parent.nodes) == 0
    assert n1 not in parent.nodes
    parent.add(n1)
    assert len(parent.nodes) == 1
    assert n1 in parent.nodes
    assert n2 not in parent.nodes
    parent.add(n2)
    assert len(parent.nodes) == 2
    assert n1 in parent.nodes
    assert n2 in parent.nodes


def test_cpa_nodes_in_acyclic_dgraph():
    p = cpa.Node('acyclic')
    a = p.add(cpa.Node('A', duration=3))
    b = p.add(cpa.Node('B', duration=3, lag=0))
    c = p.add(cpa.Node('C', duration=4, lag=0))
    d = p.add(cpa.Node('D', duration=6, lag=0))
    e = p.add(cpa.Node('E', duration=5, lag=0))
    p.link(a, b).link(a, c).link(a, d).link(b, e).link(c, e).link(d, e)
    assert p.is_acyclic() is True


def test_cpa_nodes_in_cyclic_dgraph():
    p = cpa.Node('cyclic')
    a = p.add(cpa.Node('A', duration=3))
    b = p.add(cpa.Node('B', duration=3, lag=0))
    c = p.add(cpa.Node('C', duration=4, lag=0))
    d = p.add(cpa.Node('D', duration=6, lag=0))
    e = p.add(cpa.Node('E', duration=5, lag=0))
    p.link(a, b).link(a, c).link(a, d).link(b, e).link(c, e).link(d, e).link(e, a)
    assert p.is_acyclic() is False


def test_cpa_of_micro_project():
    p = cpa.Node('micro')
    a = p.add(cpa.Node('A', duration=3))
    b = p.add(cpa.Node('B', duration=3, lag=0))
    c = p.add(cpa.Node('C', duration=4, lag=0))
    d = p.add(cpa.Node('D', duration=6, lag=0))
    e = p.add(cpa.Node('E', duration=5, lag=0))
    # a -> b -> e
    # a -> c -> e
    # a -> d -> e
    p.link(a, b).link(a, c).link(a, d).link(b, e).link(c, e).link(d, e).update_all()

    aons = {}
    for node in sorted(p.nodes, key=operator.attrgetter('name')):
        aons[node.name] = node.activity_on_node_text()

    cp = p.get_critical_path()
    assert p is not None
    aon_p = """\
+----------------+
|     DUR=14     |
+----------------+
|ES=0|     |EF=14|
|----|micro|-----|
|LS=0|     |LF=14|
+----------------+
|    DRAG=n/a    |
+----------------+
"""
    assert p.activity_on_node_text() == aon_p
    p_aon_map = {
        'duration': 14,
        'earliest_start': 0,
        'earliest_finish': 14,
        'name': 'micro',
        'latest_start': 0,
        'latest_finish': 14,
        'drag': None,
    }
    the_data = p.activity_on_node()
    assert the_data == p_aon_map
    assert json.dumps(the_data) == json.dumps(p_aon_map)  # Just to be sure :-)

    assert p.activity_on_node_strings() == tuple(row for row in aon_p.split('\n') if row)

    assert a is not None
    aon_a = """\
+-----------+
|   DUR=3   |
+-----------+
|ES=0| |EF=3|
|----|A|----|
|LS=0| |LF=3|
+-----------+
|  DRAG=n/a |
+-----------+
"""
    assert aons[a.name] == aon_a

    assert b is not None
    aon_b = """\
+-----------+
|   DUR=3   |
+-----------+
|ES=3| |EF=6|
|----|B|----|
|LS=6| |LF=9|
+-----------+
|  DRAG=n/a |
+-----------+
"""
    assert aons[b.name] == aon_b

    assert c is not None
    aon_c = """\
+-----------+
|   DUR=4   |
+-----------+
|ES=3| |EF=7|
|----|C|----|
|LS=5| |LF=9|
+-----------+
|  DRAG=n/a |
+-----------+
"""
    assert aons[c.name] == aon_c

    aon_d = """\
+-----------+
|   DUR=6   |
+-----------+
|ES=3| |EF=9|
|----|D|----|
|LS=3| |LF=9|
+-----------+
|  DRAG=n/a |
+-----------+
"""
    assert d is not None
    assert aons[d.name] == aon_d

    assert e is not None
    aon_e = """\
+------------+
|   DUR=5    |
+------------+
|ES=9| |EF=14|
|----|E|-----|
|LS=9| |LF=14|
+------------+
|  DRAG=n/a  |
+------------+
"""
    assert aons[e.name] == aon_e

    assert cp == [a, d, e]
    a_el = a.activity_on_node_strings_with_link()
    d_el = d.activity_on_node_strings_with_link()
    e_el = e.activity_on_node_strings()

    aon_dia = tuple(f'{fir}{sec}{thi}' for fir, sec, thi in zip(a_el, d_el, e_el))
    expected_diagram = """\
+-----------+    +-----------+    +------------+
|   DUR=3   |    |   DUR=6   |    |   DUR=5    |
+-----------+    +-----------+    +------------+
|ES=0| |EF=3|    |ES=3| |EF=9|    |ES=9| |EF=14|
|----|A|----| => |----|D|----| => |----|E|-----|
|LS=0| |LF=3|    |LS=3| |LF=9|    |LS=9| |LF=14|
+-----------+    +-----------+    +------------+
|  DRAG=n/a |    |  DRAG=n/a |    |  DRAG=n/a  |
+-----------+    +-----------+    +------------+
"""
    assert '\n'.join(aon_dia) + '\n' == expected_diagram

    aon_dia_text = p.aon_diagram_text(p.activity_on_node_diagram_data())
    assert aon_dia_text == expected_diagram
    assert p.aon_diagram_text_dump() == expected_diagram


def test_cpa_of_loaded_micro_project():
    p = cpa.Node('micro')
    p.load_network(str(CPA_MICRO_FIXTURE_PATH))

    aons = {}
    for node in sorted(p.nodes, key=operator.attrgetter('name')):
        aons[node.name] = node.activity_on_node_text()

    cp = p.get_critical_path()
    assert cp == [p.name_to_node['A'], p.name_to_node['D'], p.name_to_node['E']]
    assert p is not None
    aon_p = """\
+----------------+
|     DUR=14     |
+----------------+
|ES=0|     |EF=14|
|----|micro|-----|
|LS=0|     |LF=14|
+----------------+
|    DRAG=n/a    |
+----------------+
"""
    assert p.activity_on_node_text() == aon_p
    p_aon_map = {
        'duration': 14,
        'earliest_start': 0,
        'earliest_finish': 14,
        'name': 'micro',
        'latest_start': 0,
        'latest_finish': 14,
        'drag': None,
    }
    the_data = p.activity_on_node()
    assert the_data == p_aon_map
    assert json.dumps(the_data) == json.dumps(p_aon_map)  # Just to be sure :-)

    assert p.activity_on_node_strings() == tuple(row for row in aon_p.split('\n') if row)

    expected_diagram = """\
+-----------+    +-----------+    +------------+
|   DUR=3   |    |   DUR=6   |    |   DUR=5    |
+-----------+    +-----------+    +------------+
|ES=0| |EF=3|    |ES=3| |EF=9|    |ES=9| |EF=14|
|----|A|----| => |----|D|----| => |----|E|-----|
|LS=0| |LF=3|    |LS=3| |LF=9|    |LS=9| |LF=14|
+-----------+    +-----------+    +------------+
|  DRAG=n/a |    |  DRAG=n/a |    |  DRAG=n/a  |
+-----------+    +-----------+    +------------+
"""
    aon_dia_text = p.aon_diagram_text(p.activity_on_node_diagram_data())
    assert aon_dia_text == expected_diagram
    assert p.aon_diagram_text_dump() == expected_diagram


def test_model_loaded_small():
    p = cpa.Node('small-project')
    p.load_network(str(CPA_SMALL_FIXTURE_PATH))

    expected_names = CPA_SMALL_CRTICAL_PATH_EXPECTED
    assert [str(member) for member in p.get_critical_path()] == expected_names  # type: ignore
    activity_on_project = """\
+--------------------------+
|         DUR=8346         |
+--------------------------+
|ES=0|             |EF=8346|
|----|small-project|-------|
|LS=0|             |LF=8346|
+--------------------------+
|         DRAG=n/a         |
+--------------------------+
"""
    assert p.activity_on_node_text() == activity_on_project

    activity_on_node_4696 = """\
+--------------------+
|       DUR=31       |
+--------------------+
|ES=8305|    |EF=8336|
|-------|4696|-------|
|LS=8305|    |LF=8336|
+--------------------+
|      DRAG=n/a      |
+--------------------+
"""
    assert p.lookup_node('4696').activity_on_node_text() == activity_on_node_4696

    activity_on_node_4706 = """\
+--------------------+
|       DUR=10       |
+--------------------+
|ES=8336|    |EF=8346|
|-------|4706|-------|
|LS=8336|    |LF=8346|
+--------------------+
|      DRAG=n/a      |
+--------------------+
"""
    assert p.lookup_node('4706').activity_on_node_text() == activity_on_node_4706

    activity_on_node_4707 = """\
+--------------------+
|       DUR=0        |
+--------------------+
|ES=8346|    |EF=8346|
|-------|4707|-------|
|LS=8346|    |LF=8346|
+--------------------+
|      DRAG=n/a      |
+--------------------+
"""
    assert p.lookup_node('4707').activity_on_node_text() == activity_on_node_4707
