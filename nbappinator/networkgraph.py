from typing import Literal

import anywidget
import traitlets

LayoutType = Literal["force", "radial", "hierarchical", "clustered"]


class NetworkGraph(anywidget.AnyWidget):
    """D3 force-directed graph widget for NetworkX graphs."""

    nodes = traitlets.List([]).tag(sync=True)
    links = traitlets.List([]).tag(sync=True)
    width = traitlets.Int(800).tag(sync=True)
    height = traitlets.Int(600).tag(sync=True)
    layout = traitlets.Unicode("force").tag(sync=True)
    charge_strength = traitlets.Int(-70).tag(sync=True)
    link_distance = traitlets.Int(50).tag(sync=True)
    show_labels = traitlets.Bool(True).tag(sync=True)
    node_color = traitlets.Unicode("#69b3a2").tag(sync=True)
    directed = traitlets.Bool(False).tag(sync=True)
    node_size = traitlets.Int(8).tag(sync=True)
    size_by_degree = traitlets.Bool(False).tag(sync=True)

    _esm = r"""
    import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

    export function render({ model, el }) {
        const origWidth = model.get("width");
        const origHeight = model.get("height");
        let width = origWidth;
        let height = origHeight;
        const nodes = model.get("nodes");
        const links = model.get("links");
        const layout = model.get("layout");
        const chargeStrength = model.get("charge_strength");
        const linkDistance = model.get("link_distance");
        const showLabels = model.get("show_labels");
        const nodeColor = model.get("node_color");
        const directed = model.get("directed");
        const nodeSize = model.get("node_size");
        const sizeByDegree = model.get("size_by_degree");

        // Detect if we're in dark mode by checking computed background
        const isDark = window.getComputedStyle(document.body).backgroundColor
            .match(/\d+/g)?.slice(0, 3)
            .reduce((sum, v) => sum + parseInt(v), 0) < 384;
        const textColor = isDark ? "#e0e0e0" : "#333";
        const borderColor = isDark ? "#555" : "#ccc";
        const bgColor = isDark ? "#1e1e1e" : "#ffffff";

        // Create container for SVG and fullscreen button
        const container = document.createElement("div");
        container.style.cssText = "position: relative; display: inline-block;";

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("style", `border: 1px solid ${borderColor}; background: ${bgColor};`);

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
                    z-index: 9999; background: ${bgColor};
                `;
                width = window.innerWidth;
                height = window.innerHeight;
                fsBtn.innerHTML = "✕";
                fsBtn.title = "Exit fullscreen";
            } else {
                container.style.cssText = "position: relative; display: inline-block;";
                width = origWidth;
                height = origHeight;
                fsBtn.innerHTML = "⛶";
                fsBtn.title = "Toggle fullscreen";
            }
            svg.attr("width", width).attr("height", height);
            configureForces();
            simulation.alpha(0.3).restart();
        };

        // Handle Escape key to exit fullscreen
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && isFullscreen) {
                fsBtn.click();
            }
        });

        // Configure simulation based on layout type
        const simulation = d3.forceSimulation(nodes);

        function configureForces() {
            // Clear existing forces
            simulation.force("link", null);
            simulation.force("charge", null);
            simulation.force("center", null);
            simulation.force("collision", null);
            simulation.force("radial", null);
            simulation.force("x", null);
            simulation.force("y", null);

            if (layout === "radial") {
                // Radial layout: nodes arranged by degree in concentric circles
                const maxDegree = Math.max(...nodes.map(d => d.degree));
                simulation
                    .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance * 0.6).strength(0.5))
                    .force("charge", d3.forceManyBody().strength(chargeStrength * 0.5))
                    .force("radial", d3.forceRadial(
                        d => 50 + (maxDegree - d.degree) * 30,
                        width / 2,
                        height / 2
                    ).strength(0.8))
                    .force("collision", d3.forceCollide().radius(15));
            } else if (layout === "hierarchical") {
                // Hierarchical layout: high-degree nodes at top, flows down
                const maxDegree = Math.max(...nodes.map(d => d.degree));
                simulation
                    .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance * 0.75).strength(0.7))
                    .force("charge", d3.forceManyBody().strength(chargeStrength * 0.75))
                    .force("x", d3.forceX(width / 2).strength(0.1))
                    .force("y", d3.forceY(d => {
                        const rank = 1 - (d.degree / maxDegree);
                        return 50 + rank * (height - 100);
                    }).strength(0.8))
                    .force("collision", d3.forceCollide().radius(25));
            } else if (layout === "clustered") {
                // Clustered layout: tighter groups with stronger link forces
                simulation
                    .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance * 0.5).strength(1))
                    .force("charge", d3.forceManyBody().strength(chargeStrength * 1.5))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(25));
            } else {
                // Default force-directed layout
                simulation
                    .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance))
                    .force("charge", d3.forceManyBody().strength(chargeStrength))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("collision", d3.forceCollide().radius(25));
            }
        }

        configureForces();

        // Add arrow marker definition for directed graphs
        if (directed) {
            svg.append("defs").append("marker")
                .attr("id", "arrowhead")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 20)
                .attr("refY", 0)
                .attr("markerWidth", 6)
                .attr("markerHeight", 6)
                .attr("orient", "auto")
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr("fill", "#999");
        }

        const link = svg.append("g")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 2)
            .attr("marker-end", directed ? "url(#arrowhead)" : null);

        // Add hover tooltip for edges
        link.append("title")
            .text(d => {
                let text = (d.source.id || d.source) + " → " + (d.target.id || d.target);
                if (d.weight !== undefined && d.weight !== null) text += "\nWeight: " + d.weight;
                if (d.type) text += "\nType: " + d.type;
                return text;
            });

        const node = svg.append("g")
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", d => sizeByDegree ? nodeSize + d.degree * 2 : nodeSize)
            .attr("fill", nodeColor)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        const label = svg.append("g")
            .selectAll("text")
            .data(nodes)
            .join("text")
            .text(d => d.name)
            .attr("font-size", 10)
            .attr("fill", textColor)
            .attr("dx", 12)
            .attr("dy", 4)
            .attr("visibility", showLabels ? "visible" : "hidden");

        node.append("title")
            .text(d => `${d.name} (degree: ${d.degree})`);

        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        });

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        container.appendChild(svg.node());
        container.appendChild(fsBtn);
        el.appendChild(container);
    }
    """


def create_networkx_widget(
    nx_graph,
    width: int = 800,
    height: int = 600,
    layout: LayoutType = "force",
    charge_strength: int = -70,
    link_distance: int = 50,
    show_labels: bool = True,
    node_color: str = "#69b3a2",
    directed: bool = False,
    node_size: int = 8,
    size_by_degree: bool = False,
) -> NetworkGraph:
    """
    Create a D3 force-directed graph widget from a NetworkX graph.

    Args:
        nx_graph: NetworkX graph object
        width: Canvas width in pixels
        height: Canvas height in pixels
        layout: Layout algorithm - "force" (default), "radial", "hierarchical", or "clustered"
            - force: Classic force-directed layout with charge repulsion
            - radial: Nodes arranged in concentric circles by degree (high degree at center)
            - hierarchical: High-degree nodes at top, lower degree flows down
            - clustered: Tighter grouping with stronger link attraction
        charge_strength: Node repulsion force (negative). Default -70. More negative = more spread.
        link_distance: Target distance between connected nodes. Default 50.
        show_labels: Whether to show node labels. Default True.
        node_color: Node fill color (CSS color string). Default "#69b3a2".
        directed: Whether to show directional arrows on edges. Default False.
        node_size: Node radius in pixels. Default 8.
        size_by_degree: Scale node size by degree (node_size + degree * 2). Default False.

    Returns:
        NetworkGraph widget
    """
    nodes = [
        {
            "id": str(node),
            "name": str(node),
            "degree": nx_graph.degree(node),
        }
        for node in nx_graph.nodes()
    ]

    links = [
        {
            "source": str(u),
            "target": str(v),
            **{k: val for k, val in data.items()},
        }
        for u, v, data in nx_graph.edges(data=True)
    ]

    return NetworkGraph(
        nodes=nodes,
        links=links,
        width=width,
        height=height,
        layout=layout,
        charge_strength=charge_strength,
        link_distance=link_distance,
        show_labels=show_labels,
        node_color=node_color,
        directed=directed,
        node_size=node_size,
        size_by_degree=size_by_degree,
    )
