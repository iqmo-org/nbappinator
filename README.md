[![PyPI Version](https://badge.fury.io/py/nbappinator.svg)](https://pypi.python.org/pypi/nbappinator)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/nbappinator/badges/version.svg)](https://anaconda.org/conda-forge/nbappinator)
[![Tests](https://github.com/iqmo-org/nbappinator/actions/workflows/build_release.yml/badge.svg)](https://github.com/iqmo-org/nbappinator/actions/workflows/build_release.yml)
[![Tests](https://github.com/iqmo-org/nbappinator/actions/workflows/test_coverage.yml/badge.svg)](https://github.com/iqmo-org/nbappinator/actions/workflows/test_coverage.yml)

<!--[![Coverage badge](https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)-->

[![Coverage badge2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

# Introduction

nbappinator streamlines Jupyter and Voila app development through a structured, opinionated framework for UI construction. Adding a button to a tab is as simple as `app.tab(0).button("Run", on_click=callback)`.

nbappinator has three goals:

- Simplify UI development for Notebook developers by reducing the surface area of APIs to learn.
- Abstract the underlying UI components, allowing nbappinator to plug in different frameworks to achieve equivalent behavior.
- Provide a foundation to develop reusable and portable themes to improve app styling.

# Example

<!--![Example](readme_example.png)-->

# Getting Started

```py
import nbappinator as nb

def my_action(app):
    with app.messages:
        print("This message will be written to the Messages footer")
        app.tab(0).label("This is some text")

def choose_action(app):
    with app.messages:
        chosen_value = app["choose1"]
        print(f"You chose {chosen_value}")
        app.tab(1).label(f"You chose {chosen_value}")

# Create a Tabbed UI comprised of three sections:
# "Config" Header, Tabbed Pages: "First Tab" and "Second Tab", and a "Messages" Footer
myapp = nb.App(tabs=["First Tab", "Second Tab"], footer="Messages", header="Config")
myapp.config.label("This is static text in the Config section. Add global settings, buttons and other widgets here.")

# Add a button to First Tab
myapp.tab(0).label("This is the first tab")
myapp.tab(0).button("but1", on_click=my_action, label="Some button")
myapp.tab(0).label("Click the button")

# Add a dropdown selection to Second Tab
myapp.tab(1).select("choose1", options=list(range(10)), on_change=choose_action, label="Choose A Number")

# Render the app:
myapp.display()
```

## API Overview

### Creating an App

```py
app = nb.App(
    tabs=["Tab 1", "Tab 2"],  # Required: list of tab names
    header="Config",          # Optional: collapsible header section
    footer="Messages",        # Optional: collapsible footer (default)
    title="My App",           # Optional: browser title
)
```

### Accessing Sections

```py
app.config           # Header section (if configured)
app.tab(0)           # Tab by index
app.tab("Tab 1")     # Tab by name
app.footer           # Footer section
app.messages         # Output widget in footer for print statements
```

### Input Widgets

All input widgets return the page for method chaining.

```py
page.select("name", options=["a", "b"], default="a", on_change=callback)
page.combobox("name", options=["a", "b"])           # Select with text input
page.slider("name", min_val=0, max_val=100, default=50)
page.radio("name", options=["a", "b"], horizontal=True)
page.text("name", default="", multiline=False)
page.checkbox("name", default=False)
page.button("name", on_click=callback, status=True)  # status=True adds progress indicator
```

### Display Widgets

```py
page.label("Static text")
page.pre("Preformatted text")
page.html("<b>HTML content</b>")
page.separator(color="gray")
page.output("name")                # Output area for print statements
```

### Data and Charts

```py
page.dataframe("name", df, on_click=callback)
page.dataframe("name", df, tree=True, tree_column="path", enterprise=True)  # Tree requires enterprise
page.plotly(fig)
page.matplotlib(fig)
page.networkx(graph, layout="force")   # D3 force-directed graph
page.tree("name", paths=["a~b~c"], delimiter="~")  # D3 collapsible tree
```

### Standalone AG Grid

Use `create_grid()` to create an AG Grid without the App wrapper:

```py
from nbappinator import create_grid, ColMd

columns = [
    ColMd(name="price", label="Price", format="dec", precision=2),
    ColMd(name="change", label="Change %", format="perc", precision=2),
]

grid = create_grid(
    df,
    col_md=columns,
    height=400,
    enterprise=False,             # Set True for enterprise features
    license_key="",               # Your AG Grid license key
)
grid
```

### Layout

```py
row = page.row()       # Horizontal container
row.button(...)
col = page.column()    # Vertical container
```

### Callbacks

Callbacks receive the app as their only argument:

```py
def my_callback(app):
    value = app["widget_name"]       # Get widget value
    app["widget_name"] = new_value   # Set widget value
    app.status("Working...")         # Update button status
    app.done("Complete")             # Mark button as done
```

### Button with Status

```py
app.config.button("Run", on_click=run_task, status=True)

def run_task(app):
    app.status("Loading data...")
    # ... do work ...
    app.status("Processing...")
    # ... more work ...
    app.done("Complete")
```

# Examples

Interactive notebooks demonstrating nbappinator features are available in the [notebooks/](notebooks/) directory:

| Feature | Example |
|---------|---------|
| Getting Started | [1_readme_example.ipynb](notebooks/1_readme_example.ipynb) |
| Plotly Charts | [3_charts_plotly.ipynb](notebooks/3_charts_plotly.ipynb) |
| Matplotlib | [3_charts_matplotlib.ipynb](notebooks/3_charts_matplotlib.ipynb) |
| D3 Network Graphs | [4_networkx_graph.ipynb](notebooks/4_networkx_graph.ipynb) |
| Graphviz Graphs | [5_graphviz_graph.ipynb](notebooks/5_graphviz_graph.ipynb) |
| D3 Tree Widget | [6_tree_app.ipynb](notebooks/6_tree_app.ipynb) |
| AG Grid (Community) | [7_grid_anywidget.ipynb](notebooks/7_grid_anywidget.ipynb) |
| AG Grid (Enterprise) | [8_aggrid_enterprise.ipynb](notebooks/8_aggrid_enterprise.ipynb) |

# Deployment and BQuant

nbappinator was originally designed to simplify developing applications within Bloomberg's BQuant environment, which provides a managed but locked down Jupyter environment with a Voila-based deployment of applications.

# Acknowledgements

nbappinator builds on some great projects that provide useful building blocks in Jupyter, which themselves build on other great web technologies. At the same time, nbappinator is implementation agnostic - a core goal is to allow any of these components to be swapped out.

[ipyvuetify](https://ipyvuetify.readthedocs.io/en/latest/) provides the underlying UI widgets, bringing modern VUE components to Jupyter.

[AG Grid](https://ag-grid.com/) is an excellent javascript grid library. nbappinator loads AG Grid via CDN using [anywidget](https://anywidget.dev/), supporting both Community and Enterprise editions.

[Plotly](https://plotly.com/) is given first class support, although any matplotlib charting library works, such as Seaborn.

[D3.js](https://d3js.org/) powers the interactive NetworkX graph visualizations and collapsible tree widgets.

This all builds on [Jupyter](https://jupyter.org/) and [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/).

## External CDN Dependencies

At runtime, nbappinator loads the following JavaScript libraries from CDN:

- **AG Grid Community/Enterprise** from `cdn.jsdelivr.net` or `esm.sh`
- **D3.js** from `cdn.jsdelivr.net`
- **Graphviz WASM** from `cdn.jsdelivr.net` (for tree visualizations)

This means an internet connection is required when first rendering widgets that use these libraries. Bundling these dependencies locally for offline/air-gapped use is technically feasible but not yet implemented.

# Testing Notes

A significant portion of the tests are Notebook smoketests designed to exercise the code base in its entirety. The coverage report primarily reflects the percentage of the code base that the Notebooks exercise: but manual verification of the Notebook behavior is still required.

Some assertions are baked into the Notebooks, but largely its intended to ensure that all the features are exercised.
