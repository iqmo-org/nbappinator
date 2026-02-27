import logging
from typing import Optional

import ipywidgets
import plotly.colors as pc
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio

logger = logging.getLogger(__name__)


def set_default_template():
    # Use "plotly" template which adapts better to both light and dark modes
    # instead of hardcoded "plotly_white"
    pio.templates.default = "plotly"
    pio.templates[pio.templates.default].layout.colorway = px.colors.sequential.Viridis  # type: ignore


def create_widget(
    fig: go.Figure,
    setcolors: bool = False,
    png: bool = False,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> ipywidgets.Widget:
    if setcolors:
        default_color_scale = pc.DEFAULT_PLOTLY_COLORS
        numcolors = len(default_color_scale)

        line_dash_sequence = ["solid", "dot", "dash"]
        for i, trace in enumerate(fig.data):
            if hasattr(trace, "line"):
                line_dash_index = (i // numcolors) % len(line_dash_sequence)
                trace.line.dash = line_dash_sequence[line_dash_index]  # type: ignore

    if height is not None:
        fig.layout.height = height
    if width is not None:
        fig.layout.width = width

    if png:
        raise ValueError("Not supported at this time due to kaleido hanging on some environments.")

    return go.FigureWidget(fig)
