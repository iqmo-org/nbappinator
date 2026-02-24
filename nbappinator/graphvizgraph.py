from typing import Literal, Optional

import anywidget
import traitlets

LayoutEngine = Literal["dot", "neato", "fdp", "sfdp", "circo", "twopi", "osage", "patchwork"]


class GraphvizGraph(anywidget.AnyWidget):
    """Graphviz graph widget using WASM for rendering."""

    dot_source = traitlets.Unicode("digraph {}").tag(sync=True)
    width = traitlets.Int(800).tag(sync=True)
    height = traitlets.Int(600).tag(sync=True)
    engine = traitlets.Unicode("dot").tag(sync=True)
    scale = traitlets.Float(0.75).tag(sync=True)
    fit_width = traitlets.Bool(True).tag(sync=True)

    _esm = r"""
    import { Graphviz } from "https://cdn.jsdelivr.net/npm/@hpcc-js/wasm-graphviz/dist/index.js";

    export async function render({ model, el }) {
        const dotSource = model.get("dot_source");
        const width = model.get("width");
        const height = model.get("height");
        const engine = model.get("engine");
        const scale = model.get("scale");
        const fitWidth = model.get("fit_width");

        // Detect dark mode
        const isDark = window.getComputedStyle(document.body).backgroundColor
            .match(/\d+/g)?.slice(0, 3)
            .reduce((sum, v) => sum + parseInt(v), 0) < 384;
        const borderColor = isDark ? "#555" : "#ccc";
        const bgColor = isDark ? "#1e1e1e" : "#ffffff";
        const textColor = isDark ? "#e0e0e0" : "#333";

        // Create container - full width if fitWidth is true
        const container = document.createElement("div");
        container.style.cssText = `
            position: relative;
            display: block;
            width: ${fitWidth ? '100%' : width + 'px'};
            min-height: ${height}px;
            border: 1px solid ${borderColor};
            background: ${bgColor};
            overflow: auto;
        `;

        // Create fullscreen toggle button
        const fsBtn = document.createElement("button");
        fsBtn.innerHTML = "⛶";
        fsBtn.title = "Toggle fullscreen";
        fsBtn.style.cssText = `
            position: absolute; top: 8px; right: 8px; z-index: 1000;
            width: 28px; height: 28px; font-size: 16px;
            border: 1px solid ${borderColor}; border-radius: 4px;
            background: ${bgColor}; color: ${textColor};
            cursor: pointer; opacity: 0.7;
        `;
        fsBtn.onmouseenter = () => fsBtn.style.opacity = "1";
        fsBtn.onmouseleave = () => fsBtn.style.opacity = "0.7";

        let isFullscreen = false;
        fsBtn.onclick = () => {
            isFullscreen = !isFullscreen;
            if (isFullscreen) {
                container.style.cssText = `
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    z-index: 9999; background: ${bgColor}; overflow: auto;
                `;
                fsBtn.innerHTML = "✕";
                fsBtn.title = "Exit fullscreen";
            } else {
                container.style.cssText = `
                    position: relative; display: block;
                    width: ${fitWidth ? '100%' : width + 'px'};
                    min-height: ${height}px;
                    border: 1px solid ${borderColor};
                    background: ${bgColor}; overflow: auto;
                `;
                fsBtn.innerHTML = "⛶";
                fsBtn.title = "Toggle fullscreen";
            }
        };

        // Handle Escape key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && isFullscreen) {
                fsBtn.click();
            }
        });

        // SVG container
        const svgContainer = document.createElement("div");
        svgContainer.style.cssText = "padding: 10px;";

        // Loading indicator
        svgContainer.innerHTML = '<div style="color: ' + textColor + '; padding: 20px;">Loading Graphviz...</div>';

        container.appendChild(svgContainer);
        container.appendChild(fsBtn);
        el.appendChild(container);

        // Load Graphviz WASM and render
        try {
            const graphviz = await Graphviz.load();
            const svg = graphviz.layout(dotSource, "svg", engine);
            svgContainer.innerHTML = svg;

            const svgEl = svgContainer.querySelector("svg");
            if (svgEl) {
                // Apply scale transform
                if (scale !== 1.0) {
                    svgEl.style.transform = `scale(${scale})`;
                    svgEl.style.transformOrigin = "top left";
                }

                // Make SVG responsive if fitWidth
                if (fitWidth) {
                    svgEl.style.maxWidth = "100%";
                    svgEl.style.height = "auto";
                }

                // Apply dark mode styles to SVG if needed
                if (isDark) {
                    svgEl.querySelectorAll("text").forEach(t => {
                        if (t.getAttribute("fill") === "black" || !t.getAttribute("fill")) {
                            t.setAttribute("fill", textColor);
                        }
                    });
                    svgEl.querySelectorAll("polygon").forEach(p => {
                        const fill = p.getAttribute("fill");
                        if (fill === "white" || fill === "#ffffff") {
                            p.setAttribute("fill", bgColor);
                        }
                    });
                }
            }
        } catch (error) {
            svgContainer.innerHTML = '<div style="color: red; padding: 20px;">Error: ' + error.message + '</div>';
        }
    }
    """


def networkx_to_dot(
    nx_graph,
    node_attr: Optional[dict] = None,
    edge_attr: Optional[dict] = None,
    graph_attr: Optional[dict] = None,
) -> str:
    """
    Convert a NetworkX graph to DOT format string.

    Args:
        nx_graph: NetworkX graph object
        node_attr: Default attributes for all nodes (e.g., {"shape": "box"})
        edge_attr: Default attributes for all edges (e.g., {"color": "blue"})
        graph_attr: Graph-level attributes (e.g., {"rankdir": "LR"})

    Returns:
        DOT format string
    """
    is_directed = nx_graph.is_directed()
    graph_type = "digraph" if is_directed else "graph"
    edge_op = " -> " if is_directed else " -- "

    lines = [f"{graph_type} G {{"]

    # Graph attributes
    if graph_attr:
        for key, value in graph_attr.items():
            lines.append(f'    {key}="{value}";')

    # Default node attributes
    if node_attr:
        attrs = " ".join(f'{k}="{v}"' for k, v in node_attr.items())
        lines.append(f"    node [{attrs}];")

    # Default edge attributes
    if edge_attr:
        attrs = " ".join(f'{k}="{v}"' for k, v in edge_attr.items())
        lines.append(f"    edge [{attrs}];")

    # Nodes with attributes
    for node in nx_graph.nodes():
        node_data = nx_graph.nodes[node]
        node_id = str(node).replace('"', '\\"')
        if node_data:
            attrs = " ".join(f'{k}="{v}"' for k, v in node_data.items() if v is not None)
            if attrs:
                lines.append(f'    "{node_id}" [{attrs}];')
            else:
                lines.append(f'    "{node_id}";')
        else:
            lines.append(f'    "{node_id}";')

    # Edges with attributes
    for u, v, data in nx_graph.edges(data=True):
        u_id = str(u).replace('"', '\\"')
        v_id = str(v).replace('"', '\\"')
        if data:
            # Map common attributes
            edge_attrs = {}
            if "weight" in data and data["weight"] is not None:
                edge_attrs["label"] = str(data["weight"])
                edge_attrs["penwidth"] = str(max(1, min(5, data["weight"] / 20)))
            if "type" in data and data["type"] is not None:
                edge_attrs["tooltip"] = str(data["type"])
            # Add any other attributes
            for k, val in data.items():
                if k not in ("weight", "type") and val is not None:
                    edge_attrs[k] = str(val)

            if edge_attrs:
                attrs = " ".join(f'{k}="{v}"' for k, v in edge_attrs.items())
                lines.append(f'    "{u_id}"{edge_op}"{v_id}" [{attrs}];')
            else:
                lines.append(f'    "{u_id}"{edge_op}"{v_id}";')
        else:
            lines.append(f'    "{u_id}"{edge_op}"{v_id}";')

    lines.append("}")
    return "\n".join(lines)


def create_graphviz_widget(
    nx_graph,
    width: int = 800,
    height: int = 600,
    engine: LayoutEngine = "dot",
    node_attr: Optional[dict] = None,
    edge_attr: Optional[dict] = None,
    graph_attr: Optional[dict] = None,
    scale: float = 0.75,
    fit_width: bool = True,
) -> GraphvizGraph:
    """
    Create a Graphviz widget from a NetworkX graph.

    Args:
        nx_graph: NetworkX graph object
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
        node_attr: Default attributes for all nodes
        edge_attr: Default attributes for all edges
        graph_attr: Graph-level attributes
        scale: Zoom scale (default 0.75 to zoom out). 1.0 = 100%, 0.5 = 50%
        fit_width: If True, graph fills container width (default True)

    Returns:
        GraphvizGraph widget
    """
    dot_source = networkx_to_dot(nx_graph, node_attr, edge_attr, graph_attr)

    return GraphvizGraph(
        dot_source=dot_source,
        width=width,
        height=height,
        engine=engine,
        scale=scale,
        fit_width=fit_width,
    )
