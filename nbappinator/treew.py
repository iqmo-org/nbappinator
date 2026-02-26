"""D3-based tree widget for displaying hierarchical data."""

import logging
from typing import List

import anywidget
import traitlets

logger = logging.getLogger(__name__)

DEFAULT_D3_VERSION = "latest"


class D3Tree(anywidget.AnyWidget):
    """D3 collapsible tree widget with file browser style."""

    tree_data = traitlets.Dict({}).tag(sync=True)
    selected = traitlets.List([]).tag(sync=True)
    height = traitlets.Int(400).tag(sync=True)
    delimiter = traitlets.Unicode("/").tag(sync=True)
    d3_version = traitlets.Unicode(DEFAULT_D3_VERSION).tag(sync=True)

    _esm = r"""
    async function render({ model, el }) {
        const d3 = await import(`https://cdn.jsdelivr.net/npm/d3@${model.get("d3_version") || "latest"}/+esm`);
        const data = model.get("tree_data"), delim = model.get("delimiter"), h = model.get("height");
        if (!data?.name) { el.innerHTML = "<div style='padding:20px'>No tree data</div>"; return; }

        const dark = (getComputedStyle(document.body).backgroundColor.match(/\d+/g)||[]).slice(0,3).reduce((s,v)=>s+ +v,0) < 384;
        const C = dark ? {bg:"#1e1e1e",tx:"#e0e0e0",bd:"#555",hv:"#2d2d2d",sb:"#1e3a1e",sc:"#81c784"}
                       : {bg:"#fff",tx:"#333",bd:"#ccc",hv:"#f5f5f5",sb:"#e8f5e9",sc:"#4caf50"};

        let sel = new Set(model.get("selected") || []);
        const root = d3.hierarchy(data);
        const path = d => d.ancestors().reverse().filter(n=>n.data.name!=="/").map(n=>n.data.name).join(delim);

        const box = Object.assign(document.createElement("div"), {
            style: `max-height:${h}px;border:1px solid ${C.bd};background:${C.bg};overflow:auto;font:14px system-ui;padding:8px 0`
        });

        function node(d, depth) {
            const p = path(d), kids = d.children?.length;
            const div = document.createElement("div");
            const row = Object.assign(document.createElement("div"), {
                style: `display:flex;align-items:center;padding:4px 8px 4px ${8+depth*20}px;cursor:pointer;border-radius:3px;margin:1px 4px;background:${sel.has(p)?C.sb:"transparent"}`
            });
            const arr = Object.assign(document.createElement("span"), {
                textContent: kids ? "▶" : "", style: `width:16px;font-size:10px;color:${C.tx};text-align:center`
            });
            const chk = Object.assign(document.createElement("span"), {
                textContent: sel.has(p) ? "✓" : "",
                style: `width:16px;height:16px;border:2px solid ${sel.has(p)?C.sc:"#999"};border-radius:3px;margin-right:8px;display:inline-flex;align-items:center;justify-content:center;background:${sel.has(p)?C.sc:"transparent"};color:#fff;font-size:11px;cursor:pointer`
            });
            const lbl = Object.assign(document.createElement("span"), { textContent: d.data.name, style: `color:${C.tx}` });
            const sub = Object.assign(document.createElement("div"), { style: "display:none" });

            const upd = () => {
                chk.style.borderColor = sel.has(p) ? C.sc : "#999";
                chk.style.background = sel.has(p) ? C.sc : "transparent";
                chk.textContent = sel.has(p) ? "✓" : "";
                row.style.background = sel.has(p) ? C.sb : "transparent";
            };
            row.onmouseenter = () => { if (!sel.has(p)) row.style.background = C.hv; };
            row.onmouseleave = () => { row.style.background = sel.has(p) ? C.sb : "transparent"; };
            chk.onclick = e => { e.stopPropagation(); sel.has(p) ? sel.delete(p) : sel.add(p); model.set("selected", [...sel]); model.save_changes(); upd(); };

            if (kids) {
                let open = false;
                arr.style.cursor = "pointer";
                arr.onclick = e => { e.stopPropagation(); open = !open; arr.textContent = open ? "▼" : "▶"; sub.style.display = open ? "block" : "none"; };
                row.onclick = () => arr.click();
                d.children.forEach(c => sub.appendChild(node(c, depth + 1)));
            }
            div._upd = () => { upd(); [...sub.children].forEach(c => c._upd?.()); };
            row.append(arr, chk, lbl); div.append(row, sub);
            return div;
        }

        (root.data.name === "/" && root.children ? root.children : [root]).forEach(c => box.appendChild(node(c, 0)));
        el.appendChild(box);
        model.on("change:selected", () => { sel = new Set(model.get("selected") || []); [...box.children].forEach(c => c._upd?.()); });
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

    for path in sorted(paths):
        parts = path.split(delimiter)
        current = ""
        for i, part in enumerate(parts):
            parent, current = current, delimiter.join(parts[: i + 1])
            if current not in nodes:
                node = {"name": part, "children": []}
                nodes[current] = node
                (nodes.get(parent) or root)["children"].append(node)

    def clean(n):
        if n.get("children"):
            for c in n["children"]:
                clean(c)
        else:
            n.pop("children", None)

    for c in root["children"]:
        clean(c)

    return root["children"][0] if len(root["children"]) == 1 else dict(root, name="/")


def w_tree_paths(
    paths: List[str],
    pathdelim: str,
    height: int = 400,
    d3_version: str = DEFAULT_D3_VERSION,
) -> D3Tree:
    return D3Tree(
        tree_data=paths_to_tree(paths, pathdelim),
        delimiter=pathdelim,
        height=height,
        d3_version=d3_version,
    )
