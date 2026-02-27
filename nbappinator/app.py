import io
import logging
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import ipywidgets
from IPython.display import display

from . import aggrid_anywidget, graphvizgraph, networkgraph, plotly_charts, treew
from .browser_title import BrowserTitle
from .vuetify3 import (
    VuetifyButtonWidget,
    VuetifyDisplayWidget,
    VuetifyExpansionWidget,
    VuetifyFormWidget,
    VuetifyOutputWidget,
    VuetifyTabsWidget,
)

logger = logging.getLogger(__name__)


class Page:
    """A page/section in the app that can contain widgets."""

    def __init__(self, app: "App", name: str, widget: Any):
        self._app = app
        self._name = name
        self._widget = widget  # Container widget with children attribute

    def clear(self) -> "Page":
        """Clear all widgets from this page."""
        self._widget.children = []
        return self

    def _add_widget(self, widget: ipywidgets.Widget, name: Optional[str] = None) -> "Page":
        """Add a widget to this page."""
        self._widget.children = (*self._widget.children, widget)
        if name:
            self._app._widgets[name] = widget
        return self

    def _add_form_widget(
        self,
        name: str,
        widget_type: str,
        on_change: Optional[Callable] = None,
        **kwargs,
    ) -> "Page":
        """Helper to create and add a VuetifyFormWidget."""
        w = VuetifyFormWidget(widget_type=widget_type, **kwargs)
        if on_change:
            w.observe(self._app._wrap_callback_observe(on_change, name), names=["value"])
        return self._add_widget(w, name)

    def select(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiple: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a dropdown select widget."""
        return self._add_form_widget(
            name,
            "select",
            on_change,
            label=label or name,
            items=options,
            value=default,
            multiple=multiple,
            disabled=disabled,
        )

    def combobox(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiple: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a combobox (select with text input)."""
        return self._add_form_widget(
            name,
            "combobox",
            on_change,
            label=label or name,
            items=options,
            value=default,
            multiple=multiple,
            disabled=disabled,
        )

    def slider(
        self,
        name: str,
        min_val: int,
        max_val: int,
        default: Optional[int] = None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        step: int = 1,
        disabled: bool = False,
    ) -> "Page":
        """Add a slider widget."""
        return self._add_form_widget(
            name,
            "slider",
            on_change,
            label=label or name,
            min_value=float(min_val),
            max_value=float(max_val),
            value=default if default is not None else min_val,
            step=float(step),
            disabled=disabled,
        )

    def radio(
        self,
        name: str,
        options: List,
        default=None,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        horizontal: bool = False,  # noqa: ARG002 - not yet supported in Vuetify3 widget
        disabled: bool = False,
    ) -> "Page":
        """Add radio buttons."""
        return self._add_form_widget(
            name,
            "radio",
            on_change,
            label=label or name,
            items=options,
            value=default,
            disabled=disabled,
        )

    def text(
        self,
        name: str,
        default: str = "",
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        multiline: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a text input (single line or multiline)."""
        widget_type = "textarea" if multiline else "text"
        return self._add_form_widget(
            name,
            widget_type,
            on_change,
            label=label or name,
            value=default,
            disabled=disabled,
        )

    def checkbox(
        self,
        name: str,
        default: bool = False,
        label: Optional[str] = None,
        on_change: Optional[Callable] = None,
        disabled: bool = False,
    ) -> "Page":
        """Add a checkbox widget."""
        return self._add_form_widget(
            name,
            "checkbox",
            on_change,
            label=label or name,
            value=default,
            disabled=disabled,
        )

    def button(
        self,
        name: str,
        on_click: Callable,
        label: Optional[str] = None,
        status: bool = False,
        disabled: bool = False,
    ) -> "Page":
        """Add a button.

        Args:
            name: Widget name for reference
            on_click: Callback function (receives app as only argument)
            label: Button label (defaults to name)
            status: If True, adds a status display next to the button
            disabled: If True, button starts disabled
        """
        btn = VuetifyButtonWidget(
            label=label or name,
            disabled=disabled,
            variant="outlined",
            status_text="Ready" if status else "",
        )

        # Observe click count changes
        btn.observe(self._app._wrap_callback_observe(on_click, name), names=["clicked"])

        self._app._widgets[name] = btn
        if status:
            self._app._status_widgets[name] = btn  # Widget handles its own status

        return self._add_widget(btn, name)

    # --- Display widgets ---

    def label(self, text: str, name: Optional[str] = None) -> "Page":
        """Add a static text label."""
        w = VuetifyDisplayWidget(widget_type="label", content=text)
        return self._add_widget(w, name)

    def pre(self, text: str, name: Optional[str] = None) -> "Page":
        """Add preformatted text."""
        w = VuetifyDisplayWidget(widget_type="pre", content=text)
        return self._add_widget(w, name)

    def html(self, content: str, name: Optional[str] = None) -> "Page":
        """Add raw HTML content."""
        w = VuetifyDisplayWidget(widget_type="html", content=content)
        return self._add_widget(w, name)

    def separator(self, color: str = "gray") -> "Page":  # noqa: ARG002 - color not yet supported
        """Add a horizontal separator line."""
        w = VuetifyDisplayWidget(widget_type="separator")
        return self._add_widget(w)

    def output(self, name: str, max_lines: Optional[int] = None) -> "Page":  # noqa: ARG002
        """Add an output area for print statements."""
        w = VuetifyOutputWidget()
        return self._add_widget(w, name)

    # --- Data/Chart widgets ---

    def dataframe(
        self,
        name: str,
        df,
        on_click: Optional[Callable] = None,
        tree: bool = False,
        tree_column: Optional[str] = None,
        tree_delimiter: str = "~",
        column_defs: Optional[List[Dict]] = None,
        show_index: bool = False,
        pinned_rows: int = 0,
        precision: int = 2,
        multiselect: bool = False,
        grid_options: Optional[dict] = None,
        height: int = 500,
        enterprise: bool = False,
        license_key: str = "",
    ) -> "Page":
        """Add an AG Grid dataframe display.

        Args:
            name: Widget name for referencing
            df: DataFrame to display
            on_click: Callback for cell click events
            tree: Enable tree data mode (requires enterprise=True)
            tree_column: Column containing tree path
            tree_delimiter: Delimiter for tree paths
            column_defs: AG Grid column definitions (use get_column_defs() to generate, then customize)
            show_index: Show DataFrame index as column
            pinned_rows: Number of rows to pin at top
            precision: Default decimal precision
            multiselect: Enable multiple row selection
            grid_options: Additional AG Grid options
            height: Grid height in pixels
            enterprise: Enable AG Grid Enterprise features
            license_key: AG Grid Enterprise license key

        Returns:
            Page instance for chaining
        """
        if tree and tree_column and tree_column not in df.columns:
            raise ValueError(f"tree_column '{tree_column}' not found in DataFrame columns")

        w = aggrid_anywidget.create_grid(
            df,
            is_tree=tree,
            pathcol=tree_column or "path",
            pathdelim=tree_delimiter,
            column_defs=column_defs,
            showindex=show_index,
            action=on_click,
            num_toppinned_rows=pinned_rows,
            grid_options=grid_options or {},
            default_precision=precision,
            select_mode="multiple" if multiselect else "single",
            height=height,
            enterprise=enterprise,
            license_key=license_key,
        )
        return self._add_widget(w, name)

    def plotly(
        self,
        fig,
        name: Optional[str] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
    ) -> "Page":
        """Add a Plotly figure."""
        w = plotly_charts.create_widget(fig=fig, height=height, width=width)
        return self._add_widget(w, name)

    def matplotlib(
        self,
        fig,
        name: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> "Page":
        """Add a matplotlib figure."""
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        w = ipywidgets.Image(value=buf.getvalue(), format="png", width=width, height=height)
        return self._add_widget(w, name)

    def networkx(
        self,
        graph,
        name: Optional[str] = None,
        width: int = 800,
        height: int = 600,
        layout: networkgraph.LayoutType = "force",
        charge_strength: int = -200,
        link_distance: int = 80,
        show_labels: bool = True,
        node_color: str = "#69b3a2",
        directed: bool = False,
        node_size: int = 8,
        size_by_degree: bool = False,
    ) -> "Page":
        """Add a NetworkX graph visualization.

        Args:
            graph: NetworkX graph object
            name: Optional widget name for reference
            width: Canvas width in pixels
            height: Canvas height in pixels
            layout: Layout algorithm
            charge_strength: Node repulsion force (negative). More negative = more spread.
            link_distance: Target distance between connected nodes.
            show_labels: Whether to show node labels.
            node_color: Node fill color (CSS color string).
            directed: Whether to show directional arrows on edges.
            node_size: Node radius in pixels.
            size_by_degree: Scale node size by degree.
        """
        w = networkgraph.create_graph_d3(
            nx_graph=graph,
            width=width,
            height=height,
            layout=layout,
            charge_strength=charge_strength,
            link_distance=link_distance,
            show_labels=show_labels,
            node_color=node_color,
            directed=directed,
            node_size=node_size,
            size_by_degree=size_by_degree,
        )
        return self._add_widget(w, name)

    def graphviz(
        self,
        graph,
        name: Optional[str] = None,
        width: int = 800,
        height: int = 600,
        engine: graphvizgraph.LayoutEngine = "dot",
        node_attr: Optional[dict] = None,
        edge_attr: Optional[dict] = None,
        graph_attr: Optional[dict] = None,
        scale: float = 0.75,
        fit_width: bool = True,
        show_labels: bool = True,
    ) -> "Page":
        """Add a Graphviz graph visualization.

        Args:
            graph: NetworkX graph object
            name: Optional widget name for reference
            width: Canvas width in pixels (used when fit_width=False)
            height: Minimum canvas height in pixels
            engine: Graphviz layout engine:
                - dot: Hierarchical layout (default, best for DAGs)
                - neato: Spring model layout (similar to force-directed)
                - fdp: Force-directed placement
                - sfdp: Scalable force-directed (for large graphs)
                - circo: Circular layout
                - twopi: Radial layout
                - osage: Clustered layout
                - patchwork: Squarified treemap
            node_attr: Default attributes for all nodes (e.g., {"shape": "box"})
            edge_attr: Default attributes for all edges (e.g., {"color": "blue"})
            graph_attr: Graph-level attributes (e.g., {"rankdir": "LR"})
            scale: Zoom scale (default 0.75 to zoom out). 1.0 = 100%, 0.5 = 50%
            fit_width: If True, graph fills container width (default True)
            show_labels: If True, show node/edge labels (default True)
        """
        w = graphvizgraph.create_graphviz(
            nx_graph=graph,
            width=width,
            height=height,
            engine=engine,
            node_attr=node_attr,
            edge_attr=edge_attr,
            graph_attr=graph_attr,
            scale=scale,
            fit_width=fit_width,
            show_labels=show_labels,
        )
        return self._add_widget(w, name)

    def tree(
        self,
        name: str,
        paths: List[str],
        delimiter: str = "~",
    ) -> "Page":
        """Add a tree widget from paths."""
        w = treew.w_tree_paths(paths=paths, pathdelim=delimiter)
        return self._add_widget(w, name)

    # --- Layout ---

    def row(self, name: Optional[str] = None) -> "Page":
        """Add a horizontal container. Returns the new container as a Page."""
        w = ipywidgets.HBox(
            children=[],
            layout=ipywidgets.Layout(display="flex", flex_flow="row", background="transparent"),
        )
        self._add_widget(w, name)
        if name:
            self._app._containers[name] = w
        return Page(self._app, name or "", w)

    def column(self, name: Optional[str] = None) -> "Page":
        """Add a vertical container. Returns the new container as a Page."""
        w = ipywidgets.VBox(
            children=[],
            layout=ipywidgets.Layout(display="flex", flex_flow="column", background="transparent"),
        )
        self._add_widget(w, name)
        if name:
            self._app._containers[name] = w
        return Page(self._app, name or "", w)


class App:
    """
    Example:
        app = App(tabs=["Chart"], header="Config", footer="Messages")

        app.config.select("source", options=["a", "b"])
        app.config.button("Draw", on_click=draw_chart, status=True)

        def draw_chart(app):
            app.status("Drawing...")
            source = app["source"]
            app.tab("Chart").clear().plotly(fig)
            app.done()

        app.display()
    """

    def __init__(
        self,
        tabs: List[str],
        header: Optional[str] = None,
        footer: Optional[str] = "Messages",
        title: Optional[str] = None,
    ):
        """Create a new app.

        Args:
            tabs: List of tab names
            header: Optional collapsible header section name
            footer: Optional collapsible footer section name (default: "Messages")
            title: Optional browser title
        """
        self._tabs = tabs
        self._header_name = header
        self._footer_name = footer
        self._title = title

        self._widgets: dict = {}
        self._containers: dict = {}
        self._status_widgets: dict = {}  # name -> VuetifyButtonWidget with status
        self._pages: dict[str, Page] = {}
        self._current_caller: Optional[str] = None  # Track which button triggered callback

        # Build UI structure
        self._tab_widget: Optional[VuetifyTabsWidget] = None
        self._tab_contents: List[ipywidgets.VBox] = []
        self._header_widget: Optional[VuetifyExpansionWidget] = None
        self._header_content: Optional[ipywidgets.VBox] = None
        self._footer_widget: Optional[VuetifyExpansionWidget] = None
        self._footer_content: Optional[ipywidgets.VBox] = None
        self._messages: Optional[VuetifyOutputWidget] = None

        self._build_ui()

    def _build_ui(self):
        """Build the UI structure."""
        # Header (collapsible)
        if self._header_name:
            header_content = ipywidgets.VBox(
                children=[],
                layout=ipywidgets.Layout(background="transparent"),
            )
            header_content.add_class("nbapp-expansion-content")
            self._header_content = header_content
            self._pages[self._header_name] = Page(self, self._header_name, header_content)
            self._header_widget = VuetifyExpansionWidget(title=self._header_name, expanded=True)

            header_widget = self._header_widget
            assert header_widget is not None

            def on_header_expand(change):
                if change["new"]:
                    header_content.remove_class("nbapp-expansion-content--hidden")
                else:
                    header_content.add_class("nbapp-expansion-content--hidden")

            header_widget.observe(on_header_expand, names=["expanded"])

        # Tabs
        self._tab_contents = []
        for i, tab_name in enumerate(self._tabs):
            content = ipywidgets.VBox(
                children=[],
                layout=ipywidgets.Layout(background="transparent"),
            )
            content.add_class("nbapp-tab-content")
            if i != 0:
                content.add_class("nbapp-expansion-content--hidden")
            self._tab_contents.append(content)
            self._pages[tab_name] = Page(self, tab_name, content)

        if self._tabs:
            self._tab_widget = VuetifyTabsWidget(tabs=self._tabs, selected=0)
            tab_widget = self._tab_widget
            tab_contents = self._tab_contents
            assert tab_widget is not None

            def on_tab_change(change):
                for j, c in enumerate(tab_contents):
                    if j == change["new"]:
                        c.remove_class("nbapp-expansion-content--hidden")
                    else:
                        c.add_class("nbapp-expansion-content--hidden")

            tab_widget.observe(on_tab_change, names=["selected"])

        # Footer (collapsible)
        if self._footer_name:
            footer_content = ipywidgets.VBox(
                children=[],
                layout=ipywidgets.Layout(background="transparent"),
            )
            footer_content.add_class("nbapp-expansion-content")
            footer_content.add_class("nbapp-expansion-content--hidden")  # Start collapsed
            self._footer_content = footer_content
            self._pages[self._footer_name] = Page(self, self._footer_name, footer_content)
            self._footer_widget = VuetifyExpansionWidget(title=self._footer_name, expanded=False)

            footer_widget = self._footer_widget
            assert footer_widget is not None

            def on_footer_expand(change):
                if change["new"]:
                    footer_content.remove_class("nbapp-expansion-content--hidden")
                else:
                    footer_content.add_class("nbapp-expansion-content--hidden")

            footer_widget.observe(on_footer_expand, names=["expanded"])

            self._messages = VuetifyOutputWidget()
            footer_content.children = [self._messages]
            self._widgets["_messages"] = self._messages

    def _wrap_callback(self, func: Callable, caller_name: str) -> Callable:
        """Wrap a user callback for ipyvuetify on_event style."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self._current_caller = caller_name
            try:
                return func(self)
            finally:
                self._current_caller = None

        return wrapper

    def _wrap_callback_observe(self, func: Callable, caller_name: str) -> Callable:
        """Wrap a user callback for traitlets observe style."""

        @wraps(func)
        def wrapper(change):
            self._current_caller = caller_name
            try:
                return func(self)
            finally:
                self._current_caller = None

        return wrapper

    # --- Value access ---

    def __getitem__(self, name: str):
        """Get widget value by name: app['widget_name']"""
        return self.get(name)

    def __setitem__(self, name: str, value):
        """Set widget value by name: app['widget_name'] = value"""
        self.set(name, value)

    def get(self, name: str):
        """Get the current value of a widget."""
        w = self._widgets.get(name)
        if w is None:
            raise KeyError(f"No widget named '{name}'")

        # Handle different widget types
        if hasattr(w, "current_selection"):  # DataGrid
            return w.current_selection
        if hasattr(w, "value") and callable(w.value):  # Tree (value is a method)
            return w.value()
        if hasattr(w, "value"):  # Vuetify3 widgets use 'value' traitlet
            return w.value
        return None

    def set(self, name: str, value):
        """Set the value of a widget."""
        w = self._widgets.get(name)
        if w is None:
            raise KeyError(f"No widget named '{name}'")
        if hasattr(w, "value"):
            w.value = value

    # --- Page access ---

    @property
    def config(self) -> Page:
        """Access the header/config section."""
        if self._header_name:
            return self._pages[self._header_name]
        raise ValueError("No header configured. Use header='Config' in App()")

    def tab(self, name: Union[str, int]) -> Page:
        """Access a tab by name or index."""
        if isinstance(name, int):
            name = self._tabs[name]
        if name not in self._pages:
            raise KeyError(f"No tab named '{name}'")
        return self._pages[name]

    @property
    def footer(self) -> Page:
        """Access the footer section."""
        if self._footer_name:
            return self._pages[self._footer_name]
        raise ValueError("No footer configured")

    @property
    def messages(self):
        """Access the messages output widget."""
        return self._messages

    # --- Status helpers ---

    def status(self, message: str, caller: Optional[str] = None):
        """Update status for the current (or specified) button.

        Call this from within a button callback to show progress.
        """
        name = caller or self._current_caller
        if not name or name not in self._status_widgets:
            return

        btn = self._status_widgets[name]
        btn.status_text = message
        btn.loading = True

    def done(self, message: str = "Done", caller: Optional[str] = None):
        """Mark the current (or specified) button as done.

        Call this at the end of a button callback.
        """
        name = caller or self._current_caller
        if not name or name not in self._status_widgets:
            return

        btn = self._status_widgets[name]
        btn.status_text = message
        btn.loading = False

    def display(self):
        """Display the app."""
        if self._title:
            display(BrowserTitle(self._title))

        children = []

        if self._header_widget:
            children.append(self._header_widget)
        if self._header_content:
            children.append(self._header_content)

        if self._header_widget and self._tabs:
            children.append(
                ipywidgets.HTML(
                    value='<div class="nbapp-section-gap"></div>',
                    layout=ipywidgets.Layout(background="transparent"),
                )
            )

        if self._tab_widget:
            children.append(self._tab_widget)
        children.extend(self._tab_contents)

        if self._tabs and self._footer_widget:
            children.append(
                ipywidgets.HTML(
                    value='<div class="nbapp-section-gap"></div>',
                    layout=ipywidgets.Layout(background="transparent"),
                )
            )

        if self._footer_widget:
            children.append(self._footer_widget)
        if self._footer_content:
            children.append(self._footer_content)

        container = ipywidgets.VBox(
            children=children,
            layout=ipywidgets.Layout(background="transparent"),
        )
        return container
