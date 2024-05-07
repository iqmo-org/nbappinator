import logging
import ipyvuetify as v
import ipywidgets as w
import plotly.colors as pc
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import base64
from typing import Optional

logger = logging.getLogger(__name__)


def set_default_template():
    pio.templates.default = "plotly_white"
    pio.templates[pio.templates.default].layout.colorway = px.colors.sequential.Viridis  # type: ignore


def create_widget(
    fig: go.Figure,
    setcolors: bool,
    png: bool,
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> w.Widget:
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
        raise ValueError(
            "Not supported at this time due to kaleido hanging on some environments."
        )
        import kaleido  # type: ignore  # noqa

        # Kaleido is only required if png generation is needed. This ensures it is installed.
        # App may hang otherwise

        # if width is None:
        #    fig.layout.width = 900
        image_bytes = pio.to_image(fig, format="png")
        encoded_image = base64.b64encode(image_bytes).decode("utf-8")

        w = v.Html(
            tag="img",
            children=[],
            attributes={"src": "data:image/png;base64," + encoded_image},
        )

    else:
        w = go.FigureWidget(fig)

    return w
