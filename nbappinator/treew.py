import logging
import ipywidgets
import ipyvuetify as v
from ipytree import Node, Tree

logger = logging.getLogger(__name__)


def w_tree(root: str):
    rootText = f'<span style="color: green;font-weight: italic;">{root}</span>'
    tree = Tree(nodes=[Node(rootText)])
    return tree


def w_tree_paths(paths: list[str], pathdelim):
    nodes = {}  # defaultdict(default_factor=list)
    rootnodes = []

    paths = sorted(paths)
    splitpaths = [p.split(pathdelim) for p in paths]
    pathsz = zip(paths, splitpaths)

    for ps, pl in pathsz:
        plEnd = pl[-1]
        nodeText = f'<span style="color: green;font-weight: italic;">{plEnd}</span>'
        n = Node(nodeText)

        n.path = ps  # type: ignore
        if len(pl) > 1:
            n.opened = False
        nodes[ps] = n
        if len(pl) > 1:
            parent_s = pathdelim.join(pl[0:-1])
            parent_node = nodes.get(parent_s)

            if parent_node is None:
                logger.warning(f"No parent node for {parent_s}, {ps}, {pl}")
            else:
                parent_node.add_node(n)

        else:
            rootnodes.append(n)

    def tree_value(self) -> list[Node]:
        selected = []
        for node in self.nodes:
            get_selected(node, selected)
        return selected

    def get_selected(t: Node, selected: list[Node]):
        if t.selected:
            selected.append(t.path)  # type: ignore
        for c in t.nodes:
            get_selected(c, selected)

    Tree.value = tree_value  # type: ignore

    tree = Tree()
    for n in rootnodes:
        tree.add_node(n)

    return tree


def w_output():
    out = ipywidgets.Output()
    with out:
        print("Hi!")
    return out


def w_tabs(tabs: dict[str, list[ipywidgets.Widget]]):
    # Create three Tab components

    children = []

    for k, w in tabs.items():
        tab = v.Tab(children=[k])
        if isinstance(v, list):
            content = v.TabItem(
                children=w, style_="padding-left: 40%; padding-right: 10%;"
            )
        else:
            content = v.TabItem(
                children=[w], style_="padding-left: 40%; padding-right: 10%;"
            )
        children.append(tab)
        children.append(content)

    tabWidget = v.Tabs(v_model=0, children=children)  # select first tab

    return tabWidget
