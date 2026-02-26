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
    show_labels = traitlets.Bool(True).tag(sync=True)

    _esm = r"""
    import { Graphviz } from "https://cdn.jsdelivr.net/npm/@hpcc-js/wasm-graphviz/dist/index.js";
    import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

    async function render({ model, el }) {
        const dotSource = model.get("dot_source");
        const width = model.get("width");
        const height = model.get("height");
        const engine = model.get("engine");
        const scale = model.get("scale");
        const fitWidth = model.get("fit_width");
        const showLabels = model.get("show_labels");

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
            height: ${height}px;
            border: 1px solid ${borderColor};
            background: ${bgColor};
            overflow: hidden;
        `;

        // Create toolbar with buttons
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

        // Reset zoom button
        const resetBtn = document.createElement("button");
        resetBtn.innerHTML = "⟲";
        resetBtn.title = "Reset zoom";
        resetBtn.style.cssText = btnStyle;

        // Zoom in button
        const zoomInBtn = document.createElement("button");
        zoomInBtn.innerHTML = "+";
        zoomInBtn.title = "Zoom in";
        zoomInBtn.style.cssText = btnStyle;

        // Zoom out button
        const zoomOutBtn = document.createElement("button");
        zoomOutBtn.innerHTML = "−";
        zoomOutBtn.title = "Zoom out";
        zoomOutBtn.style.cssText = btnStyle;

        // Fullscreen button
        const fsBtn = document.createElement("button");
        fsBtn.innerHTML = "⛶";
        fsBtn.title = "Toggle fullscreen";
        fsBtn.style.cssText = btnStyle;

        toolbar.appendChild(resetBtn);
        toolbar.appendChild(zoomOutBtn);
        toolbar.appendChild(zoomInBtn);
        toolbar.appendChild(fsBtn);

        // Add hover effects
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

        // Handle Escape key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && isFullscreen) {
                fsBtn.click();
            }
        });

        // SVG container for pan/zoom
        const svgContainer = document.createElement("div");
        svgContainer.style.cssText = `
            width: 100%; height: 100%;
            cursor: grab;
        `;

        // Loading indicator
        svgContainer.innerHTML = '<div style="color: ' + textColor + '; padding: 20px;">Loading Graphviz...</div>';

        container.appendChild(svgContainer);
        container.appendChild(toolbar);
        el.appendChild(container);

        // Load Graphviz WASM and render
        try {
            const graphviz = await Graphviz.load();
            const svgString = graphviz.layout(dotSource, "svg", engine);
            svgContainer.innerHTML = svgString;

            const svgEl = svgContainer.querySelector("svg");
            if (svgEl) {
                // Remove explicit dimensions so preserveAspectRatio works properly
                svgEl.removeAttribute("width");
                svgEl.removeAttribute("height");
                svgEl.style.width = "100%";
                svgEl.style.height = "100%";
                svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");

                // Apply dark mode styles to SVG if needed
                if (isDark) {
                    // Fix text colors
                    svgEl.querySelectorAll("text").forEach(t => {
                        if (t.getAttribute("fill") === "black" || !t.getAttribute("fill")) {
                            t.setAttribute("fill", textColor);
                        }
                    });
                    // Fix polygon fills (background)
                    svgEl.querySelectorAll("polygon").forEach(p => {
                        const fill = p.getAttribute("fill");
                        if (fill === "white" || fill === "#ffffff") {
                            p.setAttribute("fill", bgColor);
                        }
                        // Fix polygon strokes (arrows, etc)
                        const stroke = p.getAttribute("stroke");
                        if (stroke === "black" || stroke === "#000000") {
                            p.setAttribute("stroke", textColor);
                        }
                    });
                    // Fix path strokes (edges/lines)
                    svgEl.querySelectorAll("path").forEach(p => {
                        const stroke = p.getAttribute("stroke");
                        if (stroke === "black" || stroke === "#000000") {
                            p.setAttribute("stroke", "#888888");
                        }
                    });
                    // Fix ellipse strokes (nodes)
                    svgEl.querySelectorAll("ellipse").forEach(e => {
                        const stroke = e.getAttribute("stroke");
                        if (stroke === "black" || stroke === "#000000") {
                            e.setAttribute("stroke", textColor);
                        }
                    });
                }

                // Hide labels if showLabels is false
                if (!showLabels) {
                    svgEl.querySelectorAll("text").forEach(t => {
                        t.style.display = "none";
                    });
                }

                // Setup D3 zoom/pan with wrapper group to avoid transform conflicts
                const svg = d3.select(svgEl);
                const originalG = svg.select("g");

                // Create wrapper group for zoom transforms
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

                // Use identity transform - preserveAspectRatio handles centering
                const initialTransform = d3.zoomIdentity;
                svg.call(zoom.transform, initialTransform);

                // Button handlers
                resetBtn.onclick = () => svg.transition().duration(300).call(zoom.transform, initialTransform);
                zoomInBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 1.3);
                zoomOutBtn.onclick = () => svg.transition().duration(200).call(zoom.scaleBy, 0.7);

                // Change cursor on drag
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
    )
