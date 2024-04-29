# Introduction

nbappinator is an attempt to make interactive Jupyter apps easier to develop and maintain, providing an opinionated framework to reduce the learning curve while allowing advanced users to use any types of widgets.

One major purpose for this project is to make it easier to build and deploy Jupyter applications using Voila.

# Foundation

nbappinator builds on a few great projects that provide useful building blocks in Jupyter, which themselves build on great web technologies

- [ipyvuetify](https://ipyvuetify.readthedocs.io/en/latest/): Provides the underlying UI widgets, bringing modern VUE components to Jupyter.
- [ipyaggrid](https://github.com/widgetti/ipyaggrid): Wraps the excellent [AG Grid](https://ag-grid.com/) javascript grid library. AG Grid provides some great enterprise features too.
- [ipytree](https://github.com/jupyter-widgets-contrib/ipytree): A tree widget for Jupyter

# Getting Started

```py
import nbappinator as nbapp

PAGES = ["First Tab", "Second Tab"]

def my_action(component, action, args, app: nbapp.UiModel, caller: str):
    with app.messages:
        print("This message will be written to the Messages footer")

        app.get_page(PAGES[0]).add_textstatic("ts1", "This is some text")

def choose_action(component, action, args, app: nbapp.UiModel, caller: str):
    with app.messages:
        chosen_value = app.get_values(caller)

        print(f"You chose {chosen_value}")

        app.get_page(PAGES[1]).add_textstatic(f"You chose {chosen_value}")

# Create a Tabbed UI comprised of three sections:
# "Config" Header
# Tabbed Pages: "First Tab" and "Second Tab"
# "Messages" Footer
myapp = nbapp.TabbedUiModel(pages=PAGES, log_footer = "Messages", headers=["Config"])

myapp.get_page("Config").add_textstatic("This is some static text in the Config section of the page. You could add global settings, buttons and other widgets here.")


# Add a button to First Tab
myapp.get_page(PAGES[0]).add_button(name="b1", label="Some button", action=my_action)
myapp.get_page(PAGES[0]).add_textstatic("Click the button")

# Add a dropdown selection to Second Tab
myapp.get_page(PAGES[1]).add_select(name="s1", label="Choose A Number", options=list(range(10)), action=choose_action)

# Render the app:
myapp.display()
```
