import enum
import logging
from functools import partial
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Union, Annotated, ContextManager

import ipytree
import ipyvuetify as v
import ipywidgets
from ipyvuetify import Tab, TabItem
from ipywidgets import HBox, Widget
from IPython.display import display
import traitlets


from . import aggridhelper as g
from . import treew
from . import datagrid
from . import plotly_charts as pcharts

logger = logging.getLogger(__name__)

PATHDELIM = "~"


@dataclass
class UiWidget:
    w: Widget
    name: str
    replaceable: bool = False


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

    def clear_page(self):
        self.app.clear_page(self.name)

    def add_box(
        self, name: str, horiz: bool = False, override_page: Optional[str] = None
    ):
        """Adds either a horizontal or vertical box to contain the element. It can be given a container name (to_container) so the container can be cleared and repopulated.


        Args:
            page (str): App page to add this box to
            name (str): A globally unique name for the box widget, so it can be later modified
            horiz (bool, optional): Horizontal or Vertical. Defaults to False (Vertical).
            to_container (Optional[str], optional): Creates a container, so the widgets can later be added using a container parameter. Defaults to None.

        Returns:
            _type_: _description_
        """
        if horiz:
            h = v.Html(tag="div", class_="d-flex flex-row", children=[])
        else:
            h = v.Html(tag="div", class_="d-flex flex-column", children=[])

        self.app.containers[name] = h

        return self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=h, name=name),
        )

    def add_separator(self, name: str, color: str = "gray"):
        w = v.Html(tag="hr", style_=f"border: none; border-top: 5px solid {color};")

        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_container(self, name: str):
        w = v.Container()
        self.app.containers[name] = w
        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_tree(self, name: str, paths: list[str], delim: str = PATHDELIM):
        w = treew.w_tree_paths(
            paths=paths, pathdelim=delim if delim is not None else PATHDELIM
        )
        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_textarea(
        self, name: str, label: str, disabled: bool = False, value: str = ""
    ):
        w = v.Textarea(label=label, v_model=value, disabled=disabled)
        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_textfield(
        self,
        name: str,
        label: Optional[str] = None,
        class_: Optional[str] = None,
        disabled: bool = False,
        value: str = "",
        solo=False,
        flat=False,
        override_page: Optional[str] = None,
    ):
        w = v.TextField(
            class_=class_,
            label=label,
            v_model=value,
            disabled=disabled,
            solo=solo,
            flat=flat,
        )
        return self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=w, name=name),
        )

    def add_progress(self, name: str, override_page: Optional[str] = None):
        w = v.ProgressLinear(
            class_="progress-bar", width=0, color="blue", indeterminate=True
        )
        w.hide()
        self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=w, name=name),
        )

    def add_textstatic(self, value: str = "", name: str = "anonymous"):
        w = v.CardText(children=value)
        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_textpre(self, name: str, value: str = ""):
        w = v.Html(tag="pre", children=[value], style_="max-height:80vh")
        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_output(self, name: str, max_outputs: Optional[int] = None):
        w = ipywidgets.Output()
        if max_outputs is not None:
            w.max_outputs = max_outputs  # type: ignore

        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))

    def add_plt(
        self,
        name: str,
        plt,
        width=1024,
        height=1024,
        override_page: Optional[str] = None,
    ):
        import io

        buf = io.BytesIO()
        plt.fig.savefig(buf, format="png")
        image_widget = ipywidgets.widgets.Image(
            value=buf.getvalue(), format="png", width=width, height=height
        )

        return self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=image_widget, name=name),
        )

    def add_plotly_fig(
        self,
        name: str,
        fig,
        height=None,
        width=None,
        png=False,
        setcolors=True,
        override_page: Optional[str] = None,
    ):
        w = pcharts.create_widget(
            fig=fig, setcolors=setcolors, height=height, width=width, png=png
        )

        return self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=w, name=name),
        )

    def add_select(
        self,
        name: str,
        label: str,
        disabled: bool = False,
        options: List = [],
        value=None,
        type: SelectTypes = SelectTypes.dropdown,
        multiple: bool = False,
        action: Optional[Callable] = None,
        horiz: bool = False,
        override_page: Optional[str] = None,
    ):
        if not isinstance(options, list):
            options = list(options)

        if value is True:
            value = options[0]

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
        return self.app.add(
            page=self.name,
            override_page=override_page,
            elements=UiWidget(w=w, name=name),
        )

    def add_button(
        self,
        name: str,
        action: Callable[..., None],
        disabled: bool = False,
        status: bool = False,
        label: Optional[str] = None,
        override_page: Optional[str] = None,
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

        if label is None:  # label must be set, but default to the name
            label = name

        if status:
            status_container = name + ".box"
            self.add_box(
                name=status_container, horiz=False, override_page=override_page
            )
            target = status_container
        else:
            target = self.name

        b = v.Btn(children=[label], disabled=disabled, outlined=True)

        if action is not None:
            # Use partial to pass the app & the caller name
            action = partial(action, app=self.app, caller=name)
            b.on_event("click", action)

        o = self.app.add(
            page=self.name, override_page=target, elements=UiWidget(w=b, name=name)
        )

        if status:
            self.add_textfield(
                override_page=target,
                name=name + ".status",
                label=None,
                disabled=True,
                value="Not Run",
                solo=True,
                flat=True,
                class_="for-progress",
            )

            progress_container = name + ".box.progress"
            self.add_box(name=progress_container, override_page=target, horiz=False)

            self.add_progress(
                override_page=progress_container, name=name + ".status_bar"
            )
        return o

    def add_df(
        self,
        name,
        df,
        tree: bool = False,
        pathcol: Optional[str] = None,
        perccols=[],  # deprecated
        coltypes={},  # deprecated use col_md
        col_md: List[g.ColMd] = [],
        showindex: bool = False,
        action: Optional[Callable] = None,
        num_toppinned_rows: int = 0,
        is_table_viewer_df: bool = False,
        flatten_columns: bool = True,
        pathdelim: str = PATHDELIM,
        precision: int = 2,
    ):
        if perccols or coltypes:
            raise ValueError("Deprecated, use col_md")

        grid_options = {}

        if is_table_viewer_df is True:
            grid_options["autoGroupColumnDef"] = {
                "cellRendererParams": {
                    "suppressCount": True,
                    "suppressGroupCheckbox": """function(params) {
                        return params.node.allLeafChildren.length === 1;
                    }""",
                },
            }

            grid_options["groupDefaultExpanded"] = -1

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
        )

        return self.app.add(page=self.name, elements=UiWidget(w=w, name=name))


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

    def __post_init__(self):
        for p in self.pages:
            self._add_page(title=p)

        if self.log_page is not None:
            self.get_page(self.log_page).add_output(name="m.ta")
            self.messages = self.widgets["m.ta"].w  # type: ignore

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

    def _add_page(self, title: str, children: List = []):
        self._page_widgets[title] = UiPage(
            app=self, name=title, widget=ipywidgets.VBox(children)
        )

    def add(
        self,
        page: str,
        elements: Union[UiWidget, List[UiWidget]],
        override_page: Optional[str] = None,
    ):
        page = page if override_page is None else override_page
        if page is None:
            raise ValueError(
                "Page must be set to either a page name or a container name"
            )

        if not isinstance(elements, list):
            elements_list = [elements]
        else:
            elements_list = elements

        if page in self.containers:
            logger.debug("Adding to container")
            widgets = [e.w for e in elements_list]
            self.containers[page].children = (  # type: ignore
                *self.containers[page].children,  # type: ignore
                *widgets,
            )
            for e in elements_list:
                self.widgets[e.name] = e
        else:
            logger.debug("Adding to page")

            page = self._page_widgets[page].widget  # type: ignore

            children = page.children  # type: ignore
            newchildren = []
            for e in elements_list:
                self.widgets[e.name] = e

                if e.replaceable:
                    new_container = HBox([e.w])
                    self.containers[e.name] = new_container
                    newchildren.append(new_container)
                else:
                    newchildren.append(e.w)

            page.children = (*children, *newchildren)  # type: ignore

        return elements

    def replace(self, container: str, element: UiWidget):
        if element is None:
            self.containers[container].children = []  # type: ignore
        else:
            self.containers[container].children = [element.w]  # type: ignore
            self.widgets[element.name] = element

    def get_page(self, title: str):
        if title in self._page_widgets:
            return self._page_widgets[title]
        else:
            raise ValueError(f"{title} is not a page")

    def set_value(self, name, value):
        self.widgets[name].w.v_model = value  # type: ignore

    def clear_page(self, title: str):
        p = self.get_page(title=title).widget

        if p is not None:
            # TODO: Remove from self.widgets. Not critical, since widgets are overwritten by key value
            p.children = []  # type: ignore

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
        self._page_widgets[title] = ti  # type: ignore
        self._tabWidget.children = tab_children
        if selected_tab:
            self._tabWidget.v_model = len(tab_children) / 2 - 1

        return ti  # type: ignore

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

        # display(f"Toggling {index} {name} {self.tabWidget.children[index]}")

    def toggle_tab(self, name: str, disabled: bool):
        if name in self.pages:
            index = list(self.pages).index(name)
            index *= 2
            self._tabWidget.children[index].disabled = disabled
        if self.headers is not None and name in self.headers:
            index = list(self.headers).index(name)
            self._headerWidget.children[index].disabled = disabled  # type: ignore
        # display(f"Toggling {index} {name} {self.tabWidget.children[index]}")

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
