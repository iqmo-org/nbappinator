"""
nbconvert + Playwright to convert notebooks to images for review
"""

import os
from pathlib import Path

import nbformat
import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="Visual tests require Playwright browsers (not installed in CI)",
)
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from playwright.sync_api import sync_playwright

from .env_helper import NOTEBOOK_DIR, NOTEBOOK_TIMEOUT, SKIP_NOTEBOOKS

OUTPUT_DIR = Path("test_output/visual")
RENDER_WAIT = 3000


def get_notebooks():
    notebooks = []
    for nb in NOTEBOOK_DIR.glob("**/*.ipynb"):
        if nb.name not in SKIP_NOTEBOOKS and ".ipynb_checkpoints" not in str(nb):
            notebooks.append(nb)
    return sorted(notebooks, key=lambda x: x.name)


def execute_notebook(notebook_path: Path):
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=NOTEBOOK_TIMEOUT)
    ep.preprocess(nb)

    return nb


def export_html(nb, output_dir: Path, name: str, theme: str = "light") -> Path:
    """Export executed notebook to HTML with specified theme."""
    html_dir = output_dir / "html" / theme
    html_dir.mkdir(parents=True, exist_ok=True)

    html_exporter = HTMLExporter()
    html_exporter.theme = theme
    body, _ = html_exporter.from_notebook_node(nb)

    html_path = html_dir / f"{name}.html"
    html_path.write_text(body, encoding="utf-8")

    return html_path


def screenshot_html(browser, html_path: Path, output_dir: Path, theme: str) -> Path:
    screenshot_dir = output_dir / theme
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    context = browser.new_context(
        viewport={"width": 1400, "height": 900},
    )
    page = context.new_page()

    try:
        file_url = f"file:///{html_path.absolute().as_posix()}"
        page.goto(file_url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(RENDER_WAIT)

        output_path = screenshot_dir / f"{html_path.stem}.png"
        page.screenshot(path=str(output_path), full_page=True)

        return output_path

    finally:
        context.close()


@pytest.fixture(scope="module")
def browser():
    """Create Playwright browser instance."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def executed_notebooks():
    notebooks = get_notebooks()
    results = {}

    for notebook in notebooks:
        try:
            nb = execute_notebook(notebook)
            results[notebook.stem] = {"nb": nb, "error": None}
            print(f"Executed: {notebook.name}")
        except Exception as e:
            results[notebook.stem] = {"nb": None, "error": str(e)}
            print(f"Error executing {notebook.name}: {e}")

    return results


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_visual_screenshots(browser, executed_notebooks, theme):
    errors = []
    created = []

    for name, result in executed_notebooks.items():
        if result["error"]:
            errors.append(f"{name}: Execution failed - {result['error']}")
            continue

        nb = result["nb"]
        try:
            html_path = export_html(nb, OUTPUT_DIR, name, theme)
            print(f"HTML: {html_path}")

            output_path = screenshot_html(browser, html_path, OUTPUT_DIR, theme)
            if output_path.exists():
                created.append(str(output_path))
                print(f"Screenshot: {output_path}")
            else:
                errors.append(f"{name}: Screenshot not created")
        except Exception as e:
            errors.append(f"{name}: Failed - {e}")

    print(f"\n{theme.upper()} theme: {len(created)} screenshots created")

    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    assert len(created) > 0, "No screenshots were created"


def main():

    notebooks = get_notebooks()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for notebook in notebooks:
            print(f"\nProcessing: {notebook.name}")
            try:
                nb = execute_notebook(notebook)

                for theme in ["light", "dark"]:
                    html_path = export_html(nb, OUTPUT_DIR, notebook.stem, theme)
                    print(f"  HTML ({theme}): {html_path}")

                    output_path = screenshot_html(browser, html_path, OUTPUT_DIR, theme)
                    print(f"  Screenshot ({theme}): {output_path}")

            except Exception as e:
                print(f"  Error: {e}")

        browser.close()

    print(f"\nOutput saved to: {OUTPUT_DIR.absolute()}")


if __name__ == "__main__":
    main()
