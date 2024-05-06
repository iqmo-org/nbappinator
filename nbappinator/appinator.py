import enum
import logging
import io

from functools import partial
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Union, Annotated, ContextManager

import ipytree
import ipyvuetify as v
import ipywidgets
from ipyvuetify import Tab, TabItem
from ipywidgets import Widget
from IPython.display import display
import traitlets

from . import BrowserTitle
from . import aggridhelper as g
from . import treew
from . import datagrid
from . import plotly_charts as pcharts

logger = logging.getLogger(__name__)

PATHDELIM = "~"


@dataclass
class UiWidget:
    w: Widget
    name: Optional[str]


class SelectTypes(enum.Enum):
    dropdown = 1
    combobox = 2
    slider = 3
    radio = 4


@dataclass
class UiPage:
    app: "UiModel"
    name: str

    widget: ipywidgets.Widget

    def clear(self):
        p = self.widget
        if p is not None:
            # TODO: Remove from self.widgets. Not critical, since widgets are overwritten by key value
            p.children = []  # type: ignore

    def add(self, elements: Union[UiWidget, List[UiWidget]]):
        self.app._add(target=self.name, elements=elements)

    def add_box(self, name: str, horiz: bool = False) -> "UiPage":
        """Adds either a horizontal or vertical box to contain the element.


        Args:
            page (str): App page to add this box to
            name (str): A globally unique name for the box widget, so it can be later modified
            horiz (bool, optional): Horizontal or Vertical. Defaults to False (Vertical).

        Returns:
            _type_: _description_
        """
        if horiz:
            h = v.Html(tag="div", class_="d-flex flex-row", children=[])
        else:
            h = v.Html(tag="div", class_="d-flex flex-column", children=[])

        self.app.containers[name] = h

        self.add(
            elements=UiWidget(w=h, name=name),
        )

        return UiPage(self.app, name, h)  # type: ignore

    def add_separator(self, color: str = "gray", name: Optional[str] = None):
        w = v.Html(tag="hr", style_=f"border: none; border-top: 5px solid {color};")

        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_container(self, name: str) -> "UiPage":
        """Use add_box instead"""
        w = v.Container()
        self.app.containers[name] = w
        w = self.add(
            elements=UiWidget(w=w, name=name),
        )

        return UiPage(self.app, name, w)  # type: ignore

    def add_tree(
        self,
        paths: list[str],
        delim: str = PATHDELIM,
        name: Optional[str] = None,
    ):
        w = treew.w_tree_paths(
            paths=paths, pathdelim=delim if delim is not None else PATHDELIM
        )
        self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_textarea(
        self,
        label: str,
        name: Optional[str] = None,
        disabled: bool = False,
        value: str = "",
    ):
        w = v.Textarea(label=label, v_model=value, disabled=disabled)
        self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_textfield(
        self,
        label: Optional[str] = None,
        class_: Optional[str] = None,
        disabled: bool = False,
        value: str = "",
        solo=False,
        flat=False,
        name: Optional[str] = None,
    ):
        w = v.TextField(
            class_=class_,
            label=label,
            v_model=value,
            disabled=disabled,
            solo=solo,
            flat=flat,
        )
        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_progress(
        self,
        name: Optional[str] = None,
    ):
        w = v.ProgressLinear(
            class_="progress-bar", width=0, color="blue", indeterminate=True
        )
        w.hide()
        self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_textstatic(
        self,
        value: str = "",
        name: Optional[str] = None,
    ):
        w = v.CardText(children=value)
        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_textpre(
        self,
        value: str = "",
        name: Optional[str] = None,
    ):
        w = v.Html(tag="pre", children=[value], style_="max-height:80vh")
        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_output(
        self,
        max_outputs: Optional[int] = None,
        name: Optional[str] = None,
    ):
        w = ipywidgets.Output()
        if max_outputs is not None:
            w.max_outputs = max_outputs  # type: ignore

        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_plt(
        self,
        plt,
        width=1024,
        height=1024,
        name: Optional[str] = None,
    ):

        buf = io.BytesIO()
        plt.fig.savefig(buf, format="png")
        image_widget = ipywidgets.widgets.Image(
            value=buf.getvalue(), format="png", width=width, height=height
        )

        return self.add(
            elements=UiWidget(w=image_widget, name=name),
        )

    def add_plotly_fig(
        self,
        fig,
        height=None,
        width=None,
        png=False,
        setcolors=True,
        name: Optional[str] = None,
    ):
        w = pcharts.create_widget(
            fig=fig, setcolors=setcolors, height=height, width=width, png=png
        )

        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_select(
        self,
        label: str,
        disabled: bool = False,
        options: List = [],
        value=None,
        type: SelectTypes = SelectTypes.dropdown,
        multiple: bool = False,
        action: Optional[Callable] = None,
        horiz: bool = False,
        name: Optional[str] = None,
    ):

        if type == SelectTypes.dropdown:
            w = v.Select(
                label=label,
                disabled=disabled,
                items=options,
                multiple=multiple,
                v_model=value,
            )
        elif type == SelectTypes.combobox:
            w = v.Combobox(
                label=label,
                disabled=disabled,
                items=options,
                multiple=multiple,
                v_model=value,
            )
        elif type == SelectTypes.slider:
            w = v.Slider(
                label=label,
                disabled=disabled,
                v_model=value if value is not None else options[0],
                min=options[0],
                max=options[-1],
                step=1,
                thumb_label=True,
            )
        elif type == SelectTypes.radio:
            children = [v.Radio(label=str(o), value=str(o)) for o in options]
            w = v.RadioGroup(label=label, children=children, v_model=None, row=horiz)
        else:
            raise ValueError(f"Unexpected type: {type}")

        if action is not None:
            # Use partial to pass the app & the caller name
            action = partial(action, app=self.app, caller=name)
            w.on_event("change", action)
        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_button(
        self,
        label: str,
        action: Callable[..., None],
        disabled: bool = False,
        status: bool = False,
        name: Optional[str] = None,
    ):
        """

        Args:
            page (str): The tab (page) or the container to add the button to.
            name (str): Internal name used to reference the button widget
            action (Callable): Callable that is executed when button is clicked. Must take four parameters: component, action, args, app, and caller.
            disabled (bool, optional): A disabled button cannot be clicked. Defaults to False.
            status (bool, optional): Adds a status field to the right of the button. Useful for showing feedback to user of application process. Defaults to False.
            label (Optional[str], optional): Label to show to side of button. Defaults to None.

        Returns:
            _type_: _description_
        """

        if name is None:  # label must be set, but default to the name
            name = label

        if status:
            status_container = name + ".box"
            status_box = self.add_box(name=status_container, horiz=False)
        else:
            status_box = None

        b = v.Btn(children=[label], disabled=disabled, outlined=True)

        if action is not None:
            # Use partial to pass the app & the caller name
            action = partial(action, app=self.app, caller=name)
            b.on_event("click", action)

        if status_box:
            o = status_box.add(elements=UiWidget(w=b, name=name))
        else:
            o = self.add(elements=UiWidget(w=b, name=name))

        if status:
            self.add_textfield(
                name=name + ".status",
                label=None,
                disabled=True,
                value="Not Run",
                solo=True,
                flat=True,
                class_="for-progress",
            )

            progress_container = name + ".box.progress"
            box = self.add_box(name=progress_container, horiz=False)

            box.add_progress(name=name + ".status_bar")
        return o

    def add_df(
        self,
        df,
        tree: bool = False,
        pathcol: Optional[str] = None,
        col_md: List[g.ColMd] = [],
        showindex: bool = False,
        action: Optional[Callable] = None,
        num_toppinned_rows: int = 0,
        table_viewer: bool = False,
        flatten_columns: bool = True,
        pathdelim: str = PATHDELIM,
        precision: int = 2,
        grid_options: dict = {},
        multiselect: bool = False,
        name: Optional[str] = None,
    ):
        if table_viewer is True:
            grid_options["autoGroupColumnDef"] = {
                "cellRendererParams": {
                    "suppressCount": True,
                    "suppressGroupCheckbox": """function(params) {
                        return params.node.allLeafChildren.length === 1;
                    }""",
                },
            }

            grid_options["groupDefaultExpanded"] = -1

        if multiselect:
            select_mode = "multiple"
        else:
            select_mode = None

        if tree and pathcol not in df.columns:
            raise ValueError("If tree, then pathcol must be in df.columns")

        w = g.display_ag(
            df,
            tree,
            pathcol=pathcol,
            pathdelim=pathdelim,
            showindex=showindex,
            col_md=col_md,
            action=action,
            num_toppinned_rows=num_toppinned_rows,
            grid_options=grid_options,
            flatten_columns=flatten_columns,
            default_precision=precision,
            select_mode=select_mode,
        )

        return self.add(
            elements=UiWidget(w=w, name=name),
        )

    def add_html(
        self,
        html: str,
        name: Optional[str],
    ):

        ho = HTMLOutput()
        ho.html = html
        w = UiWidget(name=name, w=ho)
        self.add(w)


@dataclass
class UiModel:

    pages: List[str]

    log_page: Optional[str] = None

    _page_widgets: Dict[str, UiPage] = field(default_factory=dict)

    messages: Annotated[ContextManager[str], field(init=False)] = field(init=False)

    # Containers are used for replacing existing elements and are optional
    containers: Dict[str, ipywidgets.Widget] = field(default_factory=dict)

    # Every UI widget is stored by name (globally in the app). This is used
    # to retrieve the current value of individual widgets.
    widgets: Dict[str, UiWidget] = field(default_factory=dict)

    title: Optional[str] = None

    def get_valuestr(self, name):
        return str(self.get_values(name))  # type: ignore

    def get_values(self, name):
        w = self.widgets[name].w

        if isinstance(w, datagrid.DataGrid):
            return w.current_selection
        if isinstance(w, ipytree.tree.Tree):
            return w.value()  # type: ignore
        else:
            return self.widgets[name].w.v_model  # type: ignore

    def _add(self, target: str, elements: Union[UiWidget, List[UiWidget]]):
        """Target can be either a Page name or a Container name"""
        if isinstance(elements, UiWidget):
            elements = [elements]

        if target in self.containers:
            logger.debug("Adding to container")
            widgets = [e.w for e in elements]
            self.containers[target].children = (  # type: ignore
                *self.containers[target].children,  # type: ignore
                *widgets,
            )
            for e in elements:
                if e.name is not None:
                    self.widgets[e.name] = e
        else:
            logger.debug("Adding to page")

            page = self._page_widgets[target].widget  # type: ignore

            children = page.children  # type: ignore
            newchildren = []
            for e in elements:
                if e.name is not None:
                    self.widgets[e.name] = e

                newchildren.append(e.w)

            page.children = (*children, *newchildren)  # type: ignore

    def get_page(self, title: Union[str, int]):
        """

        Args:
            title (Union[str, int]): If int, returns the page at the offset given from self.pages. If str, returns the page by name

        Raises:
            ValueError: An error if the input is not a Page

        """
        if isinstance(title, int):
            title = self.pages[title]

        if title in self._page_widgets:
            return self._page_widgets[title]
        else:
            raise ValueError(f"{title} is not a page")

    def set_value(self, name, value):
        self.widgets[name].w.v_model = value  # type: ignore

    def clear_messages(self):
        self.messages.clear_output()  # type: ignore

    def clear_container(self, id: str):
        w = self.widgets[id].w
        w.children = []  # type: ignore

    def update_status(self, name: str, message: str, running: bool = True):
        self.set_value(f"{name}.status", message)
        if running:
            self.start_progress(name)
        else:
            self.end_progress(name)

    def start_progress(self, name):
        self.widgets[f"{name}.status_bar"].w.show()  # type: ignore

    def end_progress(self, name):
        self.widgets[f"{name}.status_bar"].w.hide()  # type: ignore


@dataclass
class TabbedUiModel(UiModel):
    _tabWidget: v.Tabs = None  # type: ignore  - initialized in post_init
    _headerWidget: Optional[ipywidgets.Widget] = None
    _footerWidget: Optional[ipywidgets.Widget] = None
    log_footer: Optional[str] = "Messages"

    # the pages to put in the header
    headers: Optional[List[str]] = None

    def __post_init__(self):
        children = []
        if self.headers is not None:
            for header in self.headers:
                self._page_widgets[header] = UiPage(
                    app=self, name=header, widget=v.ExpansionPanelContent(children=[])
                )
                self._headerWidget = v.ExpansionPanels(
                    children=[
                        v.ExpansionPanel(
                            children=[
                                v.ExpansionPanelHeader(children=[header]),
                                self._page_widgets[header].widget,
                            ]
                        )
                    ],
                    v_model=[0],
                    multiple=True,
                )

        for tname in self.pages:
            t = Tab(children=[tname])
            ti = TabItem(children=[], style_="padding-left: 20px; padding-right: 20px;")
            children.append(t)
            children.append(ti)

            self._page_widgets[tname] = UiPage(app=self, name=tname, widget=ti)

        self._tabWidget = v.Tabs(v_model=[0], children=children)

        log_page_name = self.log_page

        if self.log_footer is not None:
            log_page_name = self.log_footer
            self._page_widgets[log_page_name] = UiPage(
                app=self,
                name=log_page_name,
                widget=v.ExpansionPanelContent(children=[]),
            )
            self._footerWidget = v.ExpansionPanels(
                children=[
                    v.ExpansionPanel(
                        children=[
                            v.ExpansionPanelHeader(children=[log_page_name]),
                            self._page_widgets[log_page_name].widget,
                        ]
                    )
                ]
            )
        if log_page_name is not None:
            self.get_page(log_page_name).add_output(name="m.ta", max_outputs=100)
            self._tabWidget = v.Tabs(v_model=[0], children=children)
            self.messages = self.widgets["m.ta"].w  # type: ignore

        if self.title is not None:
            BrowserTitle(self.title)

    def add_page(
        self, title: str, children: List = [], selected_tab=True
    ) -> ipywidgets.Widget:
        self.pages.append(title)

        tab_children = [*self._tabWidget.children]

        t = Tab(children=[title])
        ti = TabItem(
            children=children, style_="padding-left: 20px; padding-right: 20px;"
        )
        tab_children.append(t)
        tab_children.append(ti)
        self._page_widgets[title] = UiPage(app=self, name=title, widget=ti)

        self._tabWidget.children = tab_children
        if selected_tab:
            self._tabWidget.v_model = len(tab_children) / 2 - 1

        return self._page_widgets[title]  # type: ignore

    def remove_page(self, title: str):
        if title in self.pages:
            index = list(self.pages).index(title)
            self.pages.remove(title)

            tab_children = [*self._tabWidget.children]
            del tab_children[index * 2 : index * 2 + 2]

            self._page_widgets[title] = None  # type: ignore
            self._tabWidget.children = tab_children

            if self._tabWidget.v_model == index:
                self._tabWidget.v_model = index - 1

    def open_tab(self, name: str):
        if name in self.pages:
            self._tabWidget.v_model = list(self.pages).index(name)

    def toggle_tab(self, name: str, disabled: bool):
        if name in self.pages:
            index = list(self.pages).index(name)
            index *= 2
            self._tabWidget.children[index].disabled = disabled
        if self.headers is not None and name in self.headers:
            index = list(self.headers).index(name)
            self._headerWidget.children[index].disabled = disabled  # type: ignore

    def get_children(self):
        children = []
        if self._headerWidget is not None:
            children.append(self._headerWidget)
        if self._tabWidget is not None:
            children.append(self._tabWidget)
        if self._footerWidget:
            children.append(self._footerWidget)
        return children

    def display(self):
        display(ThemeFixer())
        return v.Html(
            tag="div",
            children=[
                v.Html(
                    tag="style",
                    children=[
                        """
    .vuetify-styles code, .vuetify-styles kbd, .vuetify-styles pre, .vuetify-styles samp{
        color: black !important
    }
    .v-tabs div{
        transition: none !important;
    }
    
    .for-progress .v-text-field__details{
        display: none !important;
    }
    
    .for-progress .v-input__control{
        min-height: 0px !important;
    }
    
    .for-progress input{
        text-align: center;
    }
    
    .progress-bar{
        margin-left: 10px
    }

    .vuetify-styles .v-container{
        min-width: 80vw
    }

    .ag-header {
        position: relative;
    }

   
                """
                    ],
                ),
                v.Container(children=self.get_children()),
            ],
        )


class HTMLOutput(v.VuetifyTemplate):
    html = traitlets.Unicode(default_value=None, allow_none=True).tag(sync=True)

    @traitlets.default("template")
    def _template(self):
        return """
            <template>
                <div v-html="html">
                </div>
            </template>
        """


class ThemeFixer:
    def _repr_html_(self) -> str:
        return """<script>
                    if (window.location.href.indexOf('voila') >= 0){
                        const l=document.createElement('link');
                        l.setAttribute('rel','stylesheet');  
                        l.setAttribute('type','text/css');
                        l.setAttribute('href',`${window.location.href.split('/').slice(0,7).join('/')}/static/theme-light.css`);
                        document.body.appendChild(l);
                        document.body.classList.remove('theme-dark')
                        document.body.classList.add('theme-light')
                    }
                </script>
                """
