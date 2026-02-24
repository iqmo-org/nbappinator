import argparse
import difflib
import json
import re
from pathlib import Path
from typing import List

import nbformat
from bs4 import BeautifulSoup
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor

from .env_helper import (
    BASELINE_DIR,
    NOTEBOOK_DIR,
    NOTEBOOK_TIMEOUT,
    RUNTIME_DIR,
    SEARCH,
    SKIP_NOTEBOOKS,
)

# These are ids that should be replaced
global_uuid_patterns = [
    '"[0-9a-f]{32}"',
    '"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"',
]
ignore_lines_patterns = [
    # for aggrid
    "(?is)(.*grid_data_down.*)",
    "(.*grid_data_up.*)",
    "(.*_grid_options_mono_down.*)",
    '(.*"_id": [0-9]+,.*)',
    "(.*js_helpers_custom.*)",
    "(.*js_helpers_builtin.*)",
    # for ipytree
    r"(.*\.flex[a-z\-]+\-[0-9]+\s)",
]

ignore_linep = re.compile("|".join(ignore_lines_patterns))


def prettify(body: str) -> str:
    soup = BeautifulSoup(body, "html.parser")
    for script in soup.find_all("script"):
        if script.string:
            try:
                json_object = json.loads(script.string)
                pretty_json = json.dumps(json_object, indent=4)
                script.string.replace_with(pretty_json)  # type: ignore[union-attr]
            except json.JSONDecodeError:
                pass  # Not json, ignore
    pretty_html = soup.prettify()

    return pretty_html


def sanitize_ids(body: str) -> str:
    new_uuid = 0
    for p in global_uuid_patterns:
        matches = re.findall(p, body)

        matchdict = {m: None for m in matches}  # preserve order with a dict
        for uuid in matchdict.keys():
            uuid = uuid[1:-1]
            newid = str(f"{new_uuid:032x}")
            body = body.replace(uuid, newid)
            new_uuid += 1

    return body


def generate_nbs(dir_path: "Path", sanitize: bool):
    """
    Runs all notebooks and stores their output in dir_path.
    Sanitize strips certain identifies from the document and replaces them globally.
    It's preferable to sanitize than to ignore lines, where possible.
    """

    if not dir_path.exists():
        print(f"Making directory {dir_path}")
        dir_path.mkdir()

    for notebook in NOTEBOOK_DIR.glob(SEARCH):
        if notebook.name not in SKIP_NOTEBOOKS:
            output_path: Path = dir_path / (notebook.name[0:-6] + ".html")
            print(f"Running {notebook} and writing HTML to {output_path}")
            with open(str(notebook)) as f:
                nb = nbformat.read(f, as_version=4)

            ep = ExecutePreprocessor(timeout=NOTEBOOK_TIMEOUT)
            ep.preprocess(nb)

            html_exporter = HTMLExporter()
            (body, resources) = html_exporter.from_notebook_node(nb)

            pretty_body = prettify(body)

            if sanitize:
                sanitized_body = sanitize_ids(pretty_body)
            else:
                sanitized_body = pretty_body

            output_path.write_text(sanitized_body, encoding="utf-8")
        else:
            print(f"Skipping {notebook}")


def compare(file1: "Path", file2: "Path") -> List[str]:
    """Using difflib, compares two files and returns a list of the changes.
    Lines that match the ignore_linep are skipped. Leading/trailing whitespace is ignored.

    Args:
        file1 (Path): First file
        file2 (Path): Second file

    Returns:
        List[str]: _description_
    """

    f1_lines = file1.read_text(encoding="utf-8").splitlines()
    f2_lines = file2.read_text(encoding="utf-8").splitlines()

    f1_lines = [line.strip() for line in f1_lines if not ignore_linep.match(line)]
    f2_lines = [line.strip() for line in f2_lines if not ignore_linep.match(line)]

    diff = difflib.context_diff(f1_lines, f2_lines, fromfile="file1", tofile="file2")

    return list(diff)  # type: ignore

    # Alternative: HTML report -
    # html_diff = difflib.HtmlDiff()
    # html_report = html_diff.make_file(file1_lines, file2_lines, fromdesc='File1', todesc='File2', context=True, numlines=3)
    # return html_report


def compare_all(report: bool):
    base_files = [f for f in BASELINE_DIR.glob(SEARCH.replace(".ipynb", ".html")) if f.name not in SKIP_NOTEBOOKS]

    # print(base_files)
    for f in base_files:
        compare_f = RUNTIME_DIR / f.name
        if not compare_f.exists():
            raise ValueError(f"{compare_f} does not exist")

        else:
            diff_report = compare(f, compare_f)  # type: ignore[arg-type]

            if len(diff_report) == 0:
                print(f"{f}: matches")
            else:
                print(f"{f}: doesn't match")

                if report:
                    print("\n".join(diff_report))
                    print("-" * 32)


def list_baselines():
    for f in BASELINE_DIR.glob("**/*.html"):
        print(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate_baseline", action="store_true")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--list", action="store_true")

    parser.add_argument("--sanitize", action="store_false")
    parser.add_argument("--report", action="store_true")

    args = parser.parse_args()

    sanitize = args.sanitize
    report = args.report

    if args.generate_baseline:
        print(f"Generate baseline flag is set, {sanitize=}")
        return generate_nbs(BASELINE_DIR, sanitize)  # type: ignore[arg-type]
    elif args.generate:
        print(f"Generate flag is set,  {sanitize=}")
        return generate_nbs(RUNTIME_DIR, sanitize)  # type: ignore[arg-type]
    elif args.compare:
        return compare_all(report)
    elif args.list:
        return list_baselines()

    print("No options passed, doing nothing")


if __name__ == "__main__":
    main()


# python -m tests.snapshot_mgr --list
# python -m tests.snapshot_mgr --generate_baseline
# python -m tests.snapshot_mgr --generate
# python -m tests.snapshot_mgr --compare
# python -m tests.snapshot_mgr --compare --report
