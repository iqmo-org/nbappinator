from typing import Literal, Optional

import anywidget
import traitlets

LayoutEngine = Literal["dot", "neato", "fdp", "sfdp", "circo", "twopi", "osage", "patchwork"]

DEFAULT_GRAPHVIZ_VERSION = "latest"


class GraphvizGraph(anywidget.AnyWidget):
    """Graphviz graph widget using WASM for rendering."""

    dot_source = traitlets.Unicode("digraph {}").tag(sync=True)
    width = traitlets.Int(800).tag(sync=True)
    height = traitlets.Int(600).tag(sync=True)
    engine = traitlets.Unicode("dot").tag(sync=True)
    scale = traitlets.Float(0.75).tag(sync=True)
    fit_width = traitlets.Bool(True).tag(sync=True)
    show_labels = traitlets.Bool(True).tag(sync=True)
    graphviz_version = traitlets.Unicode(DEFAULT_GRAPHVIZ_VERSION).tag(sync=True)

    _esm = r"""
    async function render({ model, el }) {
        const gvVersion = model.get("graphviz_version") || "latest";

        // Dynamic imports - graphviz version configurable, d3 always latest (only used for zoom/pan)
        const { Graphviz } = await import(`https://cdn.jsdelivr.net/npm/@hpcc-js/wasm-graphviz@${gvVersion}/dist/index.js`);
        const d3 = await import(`https://cdn.jsdelivr.net/npm/d3@latest/+esm`);

        const dotSource = model.get("dot_source");
        const width = model.get("width");
        const height = model.get("height");
        const engine = model.get("engine");
        const scale = model.get("scale");
        const fitWidth = model.get("fit_width");
        const showLabels = model.get("show_labels");

        const borderColor = "#444";
        const bgColor = "#1e1e1e";
        const textColor = "#e0e0e0";

        function isLightColor(color) {
            if (!color || color === "none") return false;
            let r, g, b;
            if (color.startsWith("#")) {
                const hex = color.slice(1);
                if (hex.length === 3) {
                    r = parseInt(hex[0] + hex[0], 16);
                    g = parseInt(hex[1] + hex[1], 16);
                    b = parseInt(hex[2] + hex[2], 16);
                } else {
                    r = parseInt(hex.slice(0, 2), 16);
                    g = parseInt(hex.slice(2, 4), 16);
                    b = parseInt(hex.slice(4, 6), 16);
                }
            } else if (color.startsWith("rgb")) {
                const match = color.match(/\d+/g);
                if (match) [r, g, b] = match.map(Number);
            } else {
                const lightColors = ["white", "yellow", "cyan", "lime", "aqua", "lightyellow", "lightblue", "lightgreen", "lightgray", "lightgrey", "beige", "ivory", "snow", "honeydew", "mintcream", "aliceblue", "lavender", "mistyrose", "lemonchiffon", "papayawhip", "seashell", "oldlace", "linen", "antiquewhite", "bisque", "peachpuff", "navajowhite", "moccasin", "cornsilk", "floralwhite", "ghostwhite", "azure", "lavenderblush"];
                return lightColors.includes(color.toLowerCase());
            }
            const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
            return luminance > 160;
        }

        const container = document.createElement("div");
        container.style.cssText = `
            position: relative;
            display: block;
            width: ${fitWidth ? '100%' : width + 'px'};
            height: ${height}px;
            border: 1px solid ${borderColor};
            background: ${bgColor};
            overflow: hidden;
        `;

        const toolbar = document.createElement("div");
        toolbar.style.cssText = `
            position: absolute; top: 8px; right: 8px; z-index: 1000;
            display: flex; gap: 4px;
        `;

        const btnStyle = `
            width: 28px; height: 28px; font-size: 14px;
            border: 1px solid ${borderColor}; border-radius: 4px;
            background: ${bgColor}; color: ${textColor};
            cursor: pointer; opacity: 0.8;
        `;

        const resetBtn = document.createElement("button");
        resetBtn.innerHTML = "⟲";
        resetBtn.title = "Reset zoom";
        resetBtn.style.cssText = btnStyle;

        const zoomInBtn = document.createElement("button");
        zoomInBtn.innerHTML = "+";
        zoomInBtn.title = "Zoom in";
        zoomInBtn.style.cssText = btnStyle;

        const zoomOutBtn = document.createElement("button");
        zoomOutBtn.innerHTML = "−";
        zoomOutBtn.title = "Zoom out";
        zoomOutBtn.style.cssText = btnStyle;

        const fsBtn = document.createElement("button");
        fsBtn.innerHTML = "⛶";
        fsBtn.title = "Toggle fullscreen";
        fsBtn.style.cssText = btnStyle;

        toolbar.appendChild(resetBtn);
        toolbar.appendChild(zoomOutBtn);
        toolbar.appendChild(zoomInBtn);
        toolbar.appendChild(fsBtn);

        [resetBtn, zoomInBtn, zoomOutBtn, fsBtn].forEach(btn => {
            btn.onmouseenter = () => btn.style.opacity = "1";
            btn.onmouseleave = () => btn.style.opacity = "0.8";
        });

        let isFullscreen = false;
        fsBtn.onclick = () => {
            isFullscreen = !isFullscreen;
            if (isFullscreen) {
                container.style.cssText = `
                    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                    z-index: 9999; background: ${bgColor}; overflow: hidden;
                `;
                fsBtn.innerHTML = "✕";
                fsBtn.title = "Exit fullscreen";
            } else {
                container.style.cssText = `
                    position: relative; display: block;
                    width: ${fitWidth ? '100%' : width + 'px'};
                    height: ${height}px;
                    border: 1px solid ${borderColor};
                    background: ${bgColor}; overflow: hidden;
                `;
                fsBtn.innerHTML = "⛶";
                fsBtn.title = "Toggle fullscreen";
            }
        };

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && isFullscreen) {
                fsBtn.click();
            }
        });

        const svgContainer = document.createElement("div");
        svgContainer.style.cssText = `
            width: 100%; height: 100%;
            cursor: grab;
        `;
        svgContainer.innerHTML = '<div style="color: ' + textColor + '; padding: 20px;">Loading Graphviz...</div>';

        container.appendChild(svgContainer);
        container.appendChild(toolbar);
        el.appendChild(container);

        try {
            const graphviz = await Graphviz.load();
            const svgString = graphviz.layout(dotSource, "svg", engine);
            svgContainer.innerHTML = svgString;

            const svgEl = svgContainer.querySelector("svg");
            if (svgEl) {
                svgEl.removeAttribute("width");
                svgEl.removeAttribute("height");
                svgEl.style.width = "100%";
                svgEl.style.height = "100%";
                svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");

                const nodeColors = new Map();
                svgEl.querySelectorAll("g.node").forEach(g => {
                    const shape = g.querySelector("ellipse, polygon, rect");
                    if (shape) {
                        const fill = shape.getAttribute("fill");
                        nodeColors.set(g, fill);
                    }
                });

                svgEl.querySelectorAll("text").forEach(t => {
                    const parentNode = t.closest("g.node");
                    if (parentNode && nodeColors.has(parentNode)) {
                        const nodeFill = nodeColors.get(parentNode);
                        t.setAttribute("fill", isLightColor(nodeFill) ? "#1a1a1a" : textColor);
                    } else if (t.getAttribute("fill") === "black" || !t.getAttribute("fill")) {
                        t.setAttribute("fill", textColor);
                    }
                });

                const polygons = svgEl.querySelectorAll("polygon");
                if (polygons.length > 0) {
                    const first = polygons[0];
                    const fill = first.getAttribute("fill");
                    if (fill === "white" || fill === "#ffffff") {
                        first.setAttribute("fill", bgColor);
                    }
                }
                polygons.forEach(p => {
                    const stroke = p.getAttribute("stroke");
                    if (stroke === "black" || stroke === "#000000") {
                        p.setAttribute("stroke", textColor);
                    }
                });

                svgEl.querySelectorAll("path").forEach(p => {
                    const stroke = p.getAttribute("stroke");
                    if (stroke === "black" || stroke === "#000000") {
                        p.setAttribute("stroke", "#888888");
                    }
                });

                svgEl.querySelectorAll("ellipse").forEach(e => {
                    const stroke = e.getAttribute("stroke");
                    if (stroke === "black" || stroke === "#000000") {
                        e.setAttribute("stroke", textColor);
                    }
                });
                if (!showLabels) {
                    svgEl.querySelectorAll("text").forEach(t => {
                        t.style.display = "none";
                    });
                }

                const svg = d3.select(svgEl);
                const originalG = svg.select("g");
                const zoomG = document.createElementNS("http://www.w3.org/2000/svg", "g");
                zoomG.setAttribute("class", "zoom-layer");
                originalG.node().parentNode.insertBefore(zoomG, originalG.node());
                zoomG.appendChild(originalG.node());

                const zoomLayer = d3.select(zoomG);

                const zoom = d3.zoom()
                    .scaleExtent([0.1, 4])
                    .on("zoom", (event) => {
                        zoomLayer.attr("transform", event.transform);
                    });

                svg.call(zoom);

                const initialTransform = d3.zoomIdentity;
                svg.call(zoom.transform, initialTransform);

                resetBtn.onclick = () => svg.transition().duration(300).call(zoom.transform, initialTransform);
                zoomInBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 1.3);
                zoomOutBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 0.7);

                svg.on("mousedown", () => svgContainer.style.cursor = "grabbing");
                svg.on("mouseup", () => svgContainer.style.cursor = "grab");
            }
        } catch (error) {
            svgContainer.innerHTML = '<div style="color: red; padding: 20px;">Error: ' + error.message + '</div>';
        }
    }

    export default { render }
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


def create_graphviz(
    nx_graph,
    width: int = 800,
    height: int = 600,
    engine: LayoutEngine = "dot",
    node_attr: Optional[dict] = None,
    edge_attr: Optional[dict] = None,
    graph_attr: Optional[dict] = None,
    scale: float = 0.75,
    fit_width: bool = True,
    show_labels: bool = True,
    graphviz_version: str = DEFAULT_GRAPHVIZ_VERSION,
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
        show_labels: If True, show node/edge labels (default True)
        graphviz_version: Graphviz WASM version to load from CDN (default: "latest").
                         Examples: "latest", "1.6.1"

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
        show_labels=show_labels,
        graphviz_version=graphviz_version,
    )
