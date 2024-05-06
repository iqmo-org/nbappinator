[![PyPI Version](https://badge.fury.io/py/nbappinator.svg)](https://pypi.python.org/pypi/nbappinator)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/nbappinator/badges/version.svg)](https://anaconda.org/conda-forge/nbappinator)
[![Tests](https://github.com/iqmo-org/nbappinator/actions/workflows/build_release.yml/badge.svg)](https://github.com/iqmo-org/nbappinator/actions/workflows/build_release.yml)
[![Tests](https://github.com/iqmo-org/nbappinator/actions/workflows/test_coverage.yml/badge.svg)](https://github.com/iqmo-org/nbappinator/actions/workflows/test_coverage.yml)

<!--[![Coverage badge](https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)-->

[![Coverage badge2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

# Introduction

nbappinator's goal is to make interactive Jupyter apps easier to develop and maintain, and reduce the learning curve involved with building & deploying Voila applications.

nbappinator provides an opinionated model for adding apps consisting of interaction widgets, such as buttons and dropdowns, along with display widgets including charts and grid / dataframe rendering.

A secondary goal is to make it easy to swap UI extensions, support different deployment environments, and insulate the developer from implementation decisions relating to web technologies.

By creating a TabbedUiModel, you can easily add new display widgets to each page/tab, and set interactions as function calls for each action.

# Foundation

nbappinator builds on a few great projects that provide useful building blocks in Jupyter, which themselves build on other great web technologies. Yet, nbappinator is intended to be implementation agnostic - a core goal is to allow any of these components to be swapped out.

- [ipyvuetify](https://ipyvuetify.readthedocs.io/en/latest/): Provides the underlying UI widgets, bringing modern VUE components to Jupyter.
- [ipyaggrid](https://github.com/widgetti/ipyaggrid): Wraps the excellent [AG Grid](https://ag-grid.com/) javascript grid library. AG Grid provides some great enterprise features too.
- [ipytree](https://github.com/jupyter-widgets-contrib/ipytree): A tree widget for Jupyter

[Plotly](https://plotly.com/) is given first class support, although any matplotlib charting library works too, such as Seaborn.

This all builds on [Jupyter](https://jupyter.org/) and [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/), of course.

# Getting Started

```py
import nbappinator as nbapp

def my_action(component, action, args, app: nbapp.UiModel, caller: str):
    with app.messages:
        print("This message will be written to the Messages footer")
        app.get_page(0).add_textstatic("This is some text")

def choose_action(component, action, args, app: nbapp.UiModel, caller: str):
    with app.messages:
        chosen_value = app.get_values(caller)
        print(f"You chose {chosen_value}")
        app.get_page(1).add_textstatic(f"You chose {chosen_value}")

# Create a Tabbed UI comprised of three sections:
# "Config" Header,  Tabbed Pages: "First Tab" and "Second Tab", and a "Messages" Footer
myapp = nbapp.TabbedUiModel(pages=["First Tab", "Second Tab"], log_footer = "Messages", headers=["Config"])
myapp.get_page("Config").add_textstatic("This is some static text in the Config section of the page. You could add global settings, buttons and other widgets here.")

# Add a button to First Tab
myapp.get_page(0).add_button(name="but1", label="Some button", action=my_action)
myapp.get_page(0).add_textstatic("Click the button")

# Add a dropdown selection to Second Tab
myapp.get_page(1).add_select(name="choose1", label="Choose A Number", options=list(range(10)), action=choose_action)

# Render the app:
myapp.display()
```

# Testing Notes

A significant portion of the tests are Notebook smoketests designed to exercise the code base in its entirety.

The coverage report primarily reflects the percentage of the code base that the Notebooks exercise: but manual verification of the Notebook behavior is still required.

Some assertions are baked into the Notebooks, but largely its intended to ensure that all the features are exercised.
