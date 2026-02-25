"""D3-based tree widget for displaying hierarchical data."""

import logging
from typing import List

import anywidget
import traitlets

logger = logging.getLogger(__name__)


class D3Tree(anywidget.AnyWidget):
    """D3 collapsible tree widget."""

    # Tree data as nested dict: {"name": "root", "children": [...]}
    tree_data = traitlets.Dict({}).tag(sync=True)
    selected = traitlets.List([]).tag(sync=True)
    height = traitlets.Int(400).tag(sync=True)
    delimiter = traitlets.Unicode("/").tag(sync=True)

    _esm = r"""
    function render({ model, el }) {
        const treeData = model.get("tree_data");
        const height = model.get("height");
        const delimiter = model.get("delimiter");

        // Detect dark mode
        const isDark = window.getComputedStyle(document.body).backgroundColor
            .match(/\d+/g)?.slice(0, 3)
            .reduce((sum, v) => sum + parseInt(v), 0) < 384;
        const borderColor = isDark ? "#555" : "#ccc";
        const bgColor = isDark ? "#1e1e1e" : "#ffffff";
        const textColor = isDark ? "#e0e0e0" : "#333";
        const hoverBg = isDark ? "#2d2d2d" : "#f5f5f5";
        const selectedBg = isDark ? "#1e3a1e" : "#e8f5e9";
        const selectedColor = isDark ? "#81c784" : "#4caf50";

        // Create container
        const container = document.createElement("div");
        container.style.cssText = `
            position: relative;
            width: 100%;
            max-height: ${height}px;
            border: 1px solid ${borderColor};
            background: ${bgColor};
            overflow: auto;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            padding: 8px 0;
        `;

        if (!treeData || !treeData.name) {
            container.innerHTML = `<div style="color: ${textColor}; padding: 20px;">No tree data</div>`;
            el.appendChild(container);
            return;
        }

        // Get selected from model
        let selectedPaths = new Set(model.get("selected") || []);

        // Build path for a node
        function getPath(node, parentPath) {
            if (parentPath) {
                return parentPath + delimiter + node.name;
            }
            return node.name;
        }

        // Create a tree node element
        function createNode(nodeData, parentPath, depth) {
            const path = getPath(nodeData, parentPath);
            const hasChildren = nodeData.children && nodeData.children.length > 0;

            const nodeEl = document.createElement("div");
            nodeEl.className = "tree-node";

            // Row container
            const row = document.createElement("div");
            row.style.cssText = `
                display: flex;
                align-items: center;
                padding: 4px 8px 4px ${8 + depth * 20}px;
                cursor: pointer;
                user-select: none;
                border-radius: 3px;
                margin: 1px 4px;
                background: ${selectedPaths.has(path) ? selectedBg : 'transparent'};
            `;

            // Hover effect
            row.onmouseenter = () => {
                if (!selectedPaths.has(path)) {
                    row.style.background = hoverBg;
                }
            };
            row.onmouseleave = () => {
                row.style.background = selectedPaths.has(path) ? selectedBg : 'transparent';
            };

            // Expand/collapse arrow
            const arrow = document.createElement("span");
            arrow.style.cssText = `
                width: 16px;
                height: 16px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 10px;
                color: ${textColor};
                flex-shrink: 0;
            `;

            let isExpanded = false;
            const childContainer = document.createElement("div");
            childContainer.style.display = "none";

            if (hasChildren) {
                arrow.textContent = "▶";
                arrow.style.cursor = "pointer";

                arrow.onclick = (e) => {
                    e.stopPropagation();
                    isExpanded = !isExpanded;
                    arrow.textContent = isExpanded ? "▼" : "▶";
                    childContainer.style.display = isExpanded ? "block" : "none";
                };
            }

            // Checkbox
            const checkbox = document.createElement("span");
            checkbox.style.cssText = `
                width: 16px;
                height: 16px;
                border: 2px solid ${selectedPaths.has(path) ? selectedColor : '#999'};
                border-radius: 3px;
                margin-right: 8px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: ${selectedPaths.has(path) ? selectedColor : 'transparent'};
                color: white;
                font-size: 11px;
                flex-shrink: 0;
                cursor: pointer;
            `;
            checkbox.textContent = selectedPaths.has(path) ? "✓" : "";

            checkbox.onclick = (e) => {
                e.stopPropagation();
                if (selectedPaths.has(path)) {
                    selectedPaths.delete(path);
                } else {
                    selectedPaths.add(path);
                }
                model.set("selected", Array.from(selectedPaths));
                model.save_changes();
                updateCheckbox();
                row.style.background = selectedPaths.has(path) ? selectedBg : hoverBg;
            };

            function updateCheckbox() {
                checkbox.style.borderColor = selectedPaths.has(path) ? selectedColor : '#999';
                checkbox.style.background = selectedPaths.has(path) ? selectedColor : 'transparent';
                checkbox.textContent = selectedPaths.has(path) ? "✓" : "";
            }

            // Label
            const label = document.createElement("span");
            label.style.cssText = `
                color: ${textColor};
                flex-grow: 1;
            `;
            label.textContent = nodeData.name;

            // Click on row toggles expand (if has children)
            row.onclick = () => {
                if (hasChildren) {
                    arrow.click();
                }
            };

            row.appendChild(arrow);
            row.appendChild(checkbox);
            row.appendChild(label);
            nodeEl.appendChild(row);

            // Create children
            if (hasChildren) {
                for (const child of nodeData.children) {
                    childContainer.appendChild(createNode(child, path, depth + 1));
                }
                nodeEl.appendChild(childContainer);
            }

            // Store update function for external updates
            nodeEl._updateSelection = () => {
                updateCheckbox();
                row.style.background = selectedPaths.has(path) ? selectedBg : 'transparent';
                if (hasChildren) {
                    for (const childEl of childContainer.children) {
                        if (childEl._updateSelection) {
                            childEl._updateSelection();
                        }
                    }
                }
            };

            return nodeEl;
        }

        // Handle single root vs multiple roots
        if (treeData.name === "/" && treeData.children) {
            // Virtual root - render children at top level
            for (const child of treeData.children) {
                container.appendChild(createNode(child, "", 0));
            }
        } else {
            // Single root
            container.appendChild(createNode(treeData, "", 0));
        }

        el.appendChild(container);

        // Listen for model changes
        model.on("change:selected", () => {
            selectedPaths = new Set(model.get("selected") || []);
            for (const nodeEl of container.children) {
                if (nodeEl._updateSelection) {
                    nodeEl._updateSelection();
                }
            }
        });
    }

    export default { render }
    """

    def value(self) -> List[str]:
        """Return list of selected paths."""
        return list(self.selected)


def paths_to_tree(paths: List[str], delimiter: str) -> dict:
    """Convert flat paths to nested tree structure for D3."""
    root = {"name": "root", "children": []}
    nodes = {"": root}

    sorted_paths = sorted(paths)

    for path in sorted_paths:
        parts = path.split(delimiter)
        current_path = ""

        for i, part in enumerate(parts):
            parent_path = current_path
            current_path = delimiter.join(parts[: i + 1])

            if current_path not in nodes:
                node = {"name": part, "children": []}
                nodes[current_path] = node

                parent = nodes.get(parent_path)
                if parent:
                    parent["children"].append(node)
                else:
                    root["children"].append(node)

    # Clean up empty children arrays
    def clean_children(node):
        if not node.get("children"):
            if "children" in node:
                del node["children"]
        else:
            for child in node["children"]:
                clean_children(child)

    for child in root["children"]:
        clean_children(child)

    # If there's only one root child, use it as the root
    if len(root["children"]) == 1:
        return root["children"][0]
    else:
        # Handle multiple roots by creating a virtual root
        root["name"] = "/"
        return root


def w_tree_paths(paths: List[str], pathdelim: str) -> D3Tree:
    """Create a D3 tree widget from paths.

    Args:
        paths: List of paths like ["org1", "org1/something", "org2"]
        pathdelim: Delimiter used in paths (e.g., "/")

    Returns:
        D3Tree widget
    """
    tree_data = paths_to_tree(paths, pathdelim)

    tree = D3Tree(
        tree_data=tree_data,
        delimiter=pathdelim,
    )

    return tree
