"""Naive Critical Path Analysis (CPA) implementation."""
import json
import pathlib
from typing import no_type_check  # Self when 3.11 is lowest bound

ActOnNodeMap = dict[str, str | int | float | None]
ActOnNodeTup = tuple[str, str, str, str, str, str, str, str, str]
ENCODING = 'utf-8'


@no_type_check
def cyclic(digraph) -> bool:
    """Determine if the directed graph has a cycle per a stack of iterators.

    The dgraph structure maps vertices to iterables of neighbouring vertices.

    # Examples:

    >>> cyclic({})
    False
    >>> cyclic({'a': ('a',)})
    True
    >>> cyclic({'a': ('z',), 'z': ('b',), 'b': ('y', 'z')})
    True
    >>> cyclic({'a': ('z',), 'z': ('b',), 'b': ('y', 'c')})
    False
    """
    visited = set()
    path = []
    paths = set(path)
    sit = [iter(digraph)]
    while sit:
        for vertex in sit[-1]:
            if vertex in paths:
                return True
            elif vertex not in visited:
                visited.add(vertex)
                path.append(vertex)
                paths.add(vertex)
                sit.append(iter(digraph.get(vertex, tuple())))
                break
        else:
            paths.discard(path.pop() if path else None)
            sit.pop()
    return False


@no_type_check
class Node:
    """Represents a task with linked nodes in an act precedence network."""

    @no_type_check
    def __init__(self, name, duration=None, lag=0) -> None:
        """Initialize the model."""
        self.parent: Node | None = None
        self.name: str = name  # model.NAME shall be unique
        self.description: str | None = None
        self.duration: float | None = duration  # model.DUR in agreed time units
        self.lag: int | float | None = lag  # preceding.finished plus in agreed time units
        self.drag: int | float | None = None  # model.DRAG in agreed time units
        self._es: int | float | None = None  # model.ES
        self.ef: int | float | None = None  # model.EF
        self.ls: int | float | None = None  # model.LS
        self.lf: int | float | None = None  # model.LF
        self._free_float: int | float | None = None  # act can delay without change start of any other act
        self._total_float: int | float | None = None  # act can delay without increase of overall project dur
        self.nodes: list[Node] = []
        self.name_to_node: dict[str, Node] = {}
        self.to_nodes: set[Node] = set()
        self.incoming_nodes: set[Node] = set()
        self.forward_pending: set[Node] = set()
        self.backward_pending: list[Node] = []
        self._critical_path = None
        self.exit_node: Node | None = None

    @no_type_check
    def lookup_node(self, name: str):
        return self.name_to_node[name]

    @no_type_check
    def get_or_create_node(self, name, **kwargs):
        try:
            return self.lookup_node(name=name)
        except KeyError:
            n = Node(name=name, **kwargs)
            self.add(n)
            return n

    @property
    def es(self) -> int | float | None:
        return self._es

    @es.setter
    def es(self, v: int | float) -> None:
        self._es = v
        if self.parent:
            self.parent.forward_pending.add(self)

    def __repr__(self) -> str:
        return str(self.name)

    def __hash__(self) -> int:
        return hash(self.name)

    @no_type_check
    def __eq__(self, other) -> bool:
        if not isinstance(other, Node):
            return False
        return self.name == other.name

    @no_type_check
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @no_type_check
    def add(self, node):
        """Includes the given node as a child node."""
        if not isinstance(node, Node):
            raise ValueError(f'tried to add non-Node instance {type(node).__name__}')
        if node.duration is None:
            raise ValueError('unspecified duration')
        if node in self.nodes:
            return
        self.nodes.append(node)
        self.name_to_node[node.name] = node
        node.parent = self
        self.forward_pending.add(node)
        self._critical_path = None
        return node

    @no_type_check
    def link(self, from_node, to_node=None) -> 'Node':
        """Directed link of two child nodes in the graph."""
        if not isinstance(from_node, Node):
            from_node = self.name_to_node[from_node]
        if not isinstance(from_node, Node):
            raise ValueError(f'tried to link from non-Node instance {type(from_node).__name__}')
        if to_node is not None:
            if not isinstance(to_node, Node):
                to_node = self.name_to_node[to_node]
            if not isinstance(to_node, Node):
                raise ValueError(f'tried to link to non-Node instance {type(to_node).__name__}')
            from_node.to_nodes.add(to_node)
            to_node.incoming_nodes.add(from_node)
        else:
            self.to_nodes.add(from_node)
            from_node.incoming_nodes.add(self)
        return self

    @no_type_check
    def load_network(self, file_path: str) -> None:
        """Load the network from JSON file with matching top level name value."""
        if not file_path.strip():
            raise ValueError('cannot load from empty file path string')
        fp = pathlib.Path(file_path)
        if not fp.is_file():
            raise ValueError('cannot load from non existing file')
        if not fp.stat().st_size:
            raise ValueError('cannot load from empty file')
        with open(fp, 'rt', encoding=ENCODING) as handle:
            network = json.load(handle)
        if not network:
            raise ValueError('cannot load from empty network')
        name = network.get('name', 'not-existing-name-key')
        if name != self.name:
            raise ValueError(f'cannot load network with name ({name}) into ({self.name})')
        x_nodes = {}
        for x_key, x_node in network.get('nodes', {}).items():
            duration = x_node.get('duration', None)
            lag = x_node.get('lag', 0)
            x_nodes[x_key] = self.add(Node(x_key, duration=duration, lag=lag))
        for edge in network.get('edges', []):
            if len(edge) < 2:
                if not edge:
                    raise ValueError('cannot build an empty edge')
                raise ValueError(f'cannot build directed edge from ({edge[0]}) without a target')
            if len(edge) == 2:
                if any(edg not in x_nodes for edg in edge):
                    raise ValueError(f'cannot build edge with nodes not in {x_nodes}')
                self.link(x_nodes[edge[0]], x_nodes[edge[1]])
            else:
                raise NotImplementedError('Compressed edges notation not yet implemented.')
        self.update_all()

    @property
    @no_type_check
    def first_nodes(self):
        """Child nodes that have no in-bound dependencies."""
        first = set(self.nodes)
        for node in self.nodes:
            first.difference_update(node.to_nodes)
        return first

    @property
    @no_type_check
    def last_nodes(self):
        """Child nodes that have to out-bound dependencies."""
        return [node for node in self.nodes if not node.to_nodes]

    @no_type_check
    def update_forward(self) -> None:
        """Updates forward timing calculations for the current node assuming min(es) is set."""
        changed = False
        if self.es is not None and self.duration is not None:
            self.ef = self.es + self.duration
            changed = True

        if changed:
            for to_node in self.to_nodes:
                if to_node == self:
                    continue
                add_some_lag = self.ef + to_node.lag
                to_node.es = add_some_lag if to_node.es is None else max(to_node.es, add_some_lag)

                if self.parent:
                    self.parent.forward_pending.add(to_node)

            if self.parent:
                self.parent.backward_pending.append(self)

    @no_type_check
    def update_backward(self) -> None:
        """Updates backward timing calculations for the current node."""
        if self.lf is None:
            if self.to_nodes:
                self.lf = min(target.ls for target in self.to_nodes)
            else:
                self.lf = self.ef
            if self.lf is None:
                raise ValueError('No latest finish time found')
        self.ls = self.lf - self.duration

    @no_type_check
    def add_exit(self) -> None:
        """Links all leaf nodes to a common exit node."""
        if self.exit_node is None:
            self.exit_node = Node('COMMON_EXIT', duration=0)
            self.add(self.exit_node)
        for node in self.nodes:
            if node is self.exit_node:
                continue
            if not node.to_nodes:
                self.link(from_node=node, to_node=self.exit_node)

    @no_type_check
    def update_all(self) -> None:
        """Updates timing calculations for all children nodes."""
        if not self.is_acyclic():
            raise TypeError('Network contains cycles')

        for node in list(self.forward_pending.intersection(self.first_nodes)):
            node.es = self.lag + node.lag
            node.update_forward()
            self.forward_pending.remove(node)

        forward_priors = set()
        while self.forward_pending:
            q = set(self.forward_pending)
            self.forward_pending.clear()
            while q:
                node = q.pop()
                if node in forward_priors:
                    continue
                node.update_forward()

        backward_priors = set()
        while self.backward_pending:
            node = self.backward_pending.pop()
            if node in backward_priors:
                continue
            node.update_backward()

        duration, path, priors = self.get_critical_path(as_item=True)
        self._critical_path = duration, path, priors
        self.duration = duration
        self.es = path[0].es
        self.ls = path[0].ls
        self.ef = path[-1].ef
        self.lf = path[-1].lf

    @no_type_check
    def get_critical_path(self, as_item: bool = False):
        """Finds the longest path in among the child nodes."""
        if self._critical_path is not None:
            return self._critical_path[1]
        longest = None
        q = [(_.duration, [_], set([_])) for _ in self.first_nodes]
        while q:
            item = length, path, priors = q.pop(0)
            if longest is None:
                longest = item
            else:
                try:
                    longest = max(longest, item)
                except TypeError:
                    longest = longest
            for to_node in path[-1].to_nodes:
                if to_node in priors:
                    continue
                q.append((length + to_node.duration, path + [to_node], priors.union([to_node])))
        if longest is None:
            return
        elif as_item:
            return longest
        else:
            return longest[1]

    @no_type_check
    def activity(self, node) -> ActOnNodeMap:
        """Provide the activity-on-node element of given node as JSON serializable dict."""
        return {
            'duration': node.duration,
            'earliest_start': node.es,
            'earliest_finish': node.ef,
            'name': node.name,
            'latest_start': node.ls,
            'latest_finish': node.lf,
            'drag': node.drag,
        }

    @no_type_check
    def activity_on_node(self) -> ActOnNodeMap:
        """Provide the activity-on-node element as JSON serializable dict."""
        return self.activity(self)

    @no_type_check
    def activity_on_node_diagram_data(self) -> list[ActOnNodeMap]:
        """Provide the activity-on-node diagram as JSON serializable list of dicts."""
        cp = self.get_critical_path()
        return [self.activity(node) for node in cp] if cp else []

    @staticmethod
    @no_type_check
    def aon_strings(aon: ActOnNodeMap) -> ActOnNodeTup:
        """Provide the activity-on-node element from map data as 9-tuple of strings.

        Example:

        cf. example of activity_on_node_strings method
        """
        duration = aon['duration']
        earliest_start = aon['earliest_start']
        earliest_finish = aon['earliest_finish']
        name = aon['name']
        latest_start = aon['latest_start']
        latest_finish = aon['latest_finish']
        drag = aon['drag']

        lk_width = max(len(f'{lk}=') for lk in ('ES', 'EF', 'LS', 'LF'))
        sp, hr, vr = ' ', '-', '|'
        bd_width = len(vr)
        max_width, lc_max_width, cc_max_width, rc_max_width = 0, 0, 0, 0
        lc_max_width = max(len(str(earliest_start)), len(str(latest_start))) + lk_width
        cc_max_width = len(str(name))
        rc_max_width = max(len(str(earliest_finish)), len(str(latest_finish))) + lk_width
        max_width = sum((lc_max_width, cc_max_width, rc_max_width)) + 2 * bd_width  # inner borders

        section_sep = f'+{hr * max_width}+'

        dur_disp = f'DUR={duration}'
        dur_sect = f'{vr}{dur_disp.center(max_width, sp)}{vr}'
        es_disp = f'ES={earliest_start}'
        ef_disp = f'EF={earliest_finish}'
        es_ef_sects = (
            f'{vr}{es_disp.center(lc_max_width, sp)}'
            f'{vr}{sp.center(cc_max_width, sp)}'
            f'{vr}{ef_disp.center(rc_max_width, sp)}{vr}'
        )
        name_sect = (
            f'{vr}{hr.center(lc_max_width, hr)}'
            f'{vr}{str(name).center(cc_max_width, sp)}'
            f'{vr}{hr.center(rc_max_width, hr)}{vr}'
        )
        ls_disp = f'LS={latest_start}'
        lf_disp = f'LF={latest_finish}'
        ls_lf_sects = (
            f'{vr}{ls_disp.center(lc_max_width, sp)}'
            f'{vr}{sp.center(cc_max_width, sp)}'
            f'{vr}{lf_disp.center(rc_max_width, sp)}{vr}'
        )
        drg_disp = f'DRAG={drag if drag is not None else "n/a"}'
        drg_sect = f'{vr}{drg_disp.center(max_width, sp)}{vr}'

        return (
            section_sep,
            dur_sect,
            section_sep,
            es_ef_sects,
            name_sect,
            ls_lf_sects,
            section_sep,
            drg_sect,
            section_sep,
        )

    def activity_on_node_strings(self) -> ActOnNodeTup:
        """Provide the activity-on-node element as 9-tuple of strings for e.g. linking along the critical path.

        Example:

        +-----------------------+  # section_sep
        |        DUR=31         |  # dur_sect
        +-----------------------+  # section_sep
        |ES=8308|       |EF=8339|  # es_ef_sects
        |-------|  4696 |-------|  # name_sect
        |LS=8308|       |LF=8339|  # ls_lf_sects
        +-----------------------+  # section_sep
        |       DRAG=None       |  # drg_sect
        +-----------------------+  # section_sep
        """
        lk_width = max(len(f'{lk}=') for lk in ('ES', 'EF', 'LS', 'LF'))
        sp, hr, vr = ' ', '-', '|'
        bd_width = len(vr)
        max_width, lc_max_width, cc_max_width, rc_max_width = 0, 0, 0, 0
        lc_max_width = max(len(str(self.es)), len(str(self.ls))) + lk_width
        cc_max_width = len(str(self.name))
        rc_max_width = max(len(str(self.ef)), len(str(self.lf))) + lk_width
        max_width = sum((lc_max_width, cc_max_width, rc_max_width)) + 2 * bd_width  # inner borders

        section_sep = f'+{hr * max_width}+'

        dur_disp = f'DUR={self.duration}'
        dur_sect = f'{vr}{dur_disp.center(max_width, sp)}{vr}'
        es_disp = f'ES={self.es}'
        ef_disp = f'EF={self.ef}'
        es_ef_sects = (
            f'{vr}{es_disp.center(lc_max_width, sp)}'
            f'{vr}{sp.center(cc_max_width, sp)}'
            f'{vr}{ef_disp.center(rc_max_width, sp)}{vr}'
        )
        name_sect = (
            f'{vr}{hr.center(lc_max_width, hr)}'
            f'{vr}{str(self.name).center(cc_max_width, sp)}'
            f'{vr}{hr.center(rc_max_width, hr)}{vr}'
        )
        ls_disp = f'LS={self.ls}'
        lf_disp = f'LF={self.lf}'
        ls_lf_sects = (
            f'{vr}{ls_disp.center(lc_max_width, sp)}'
            f'{vr}{sp.center(cc_max_width, sp)}'
            f'{vr}{lf_disp.center(rc_max_width, sp)}{vr}'
        )
        drg_disp = f'DRAG={self.drag if self.drag is not None else "n/a"}'
        drg_sect = f'{vr}{drg_disp.center(max_width, sp)}{vr}'

        return (
            section_sep,
            dur_sect,
            section_sep,
            es_ef_sects,
            name_sect,
            ls_lf_sects,
            section_sep,
            drg_sect,
            section_sep,
        )

    @staticmethod
    def aon_strings_with_link(aon_strings: ActOnNodeTup) -> ActOnNodeTup:
        """DRY."""
        arrow = ' => '
        spacer = ' ' * len(arrow)
        link: ActOnNodeTup = (spacer, spacer, spacer, spacer, arrow, spacer, spacer, spacer, spacer)
        return tuple(f'{rec}{spc}' for rec, spc in zip(aon_strings, link))  # type: ignore

    @staticmethod
    def aon_diagram_text(aons: list[ActOnNodeMap]) -> str:
        """Build a text representation for a path with activity-on-nodes linked directionally."""
        dia = []
        for aon in aons[:-1]:
            dia.append(Node.aon_strings_with_link(Node.aon_strings(aon)))
        dia.append(Node.aon_strings(aons[-1]))
        return '\n'.join(''.join(row) for row in zip(*dia)) + '\n'

    def aon_diagram_text_dump(self) -> str:
        """Build a text representation for the critical path with activity-on-nodes linked directionally."""
        return self.aon_diagram_text(self.activity_on_node_diagram_data())

    def activity_on_node_strings_with_link(self) -> ActOnNodeTup:
        """DRY."""
        return self.aon_strings_with_link(self.activity_on_node_strings())

    def activity_on_node_text(self) -> str:
        """Provide the activity-on-node element as string with trailing newline for e.g. a textual diagram."""
        return '\n'.join(self.activity_on_node_strings()) + '\n'

    def is_acyclic(self) -> bool:
        g = dict((node.name, tuple(child.name for child in node.to_nodes)) for node in self.nodes)
        return not cyclic(g)
