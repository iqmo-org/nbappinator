import logging
import os
from pathlib import Path

import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor

from .env_helper import NOTEBOOK_DIR, NOTEBOOK_TIMEOUT, SEARCH, SKIP_NOTEBOOKS

logger = logging.getLogger(__name__)


# Run this test for every ipynb file in notebook directory
@pytest.mark.parametrize(
    "notebook",
    [
        f
        for f in NOTEBOOK_DIR.glob(SEARCH)
        if f.name not in SKIP_NOTEBOOKS
        and ".ipynb_checkpoints" not in str(f.absolute())
    ],
)
def test_notebook_execution(notebook: Path, pytestconfig):
    """Verifies that the notebook runs to completion without an Exception.

    This test is a low standard: it doesn't verify the notebooks are usable. It's useful
    with coverage.py to verify that notebooks execute all code paths.

    To make this method more robust: add assertions to the end of notebooks
    `assert xyz`

    Or, alternatively, use `test_notebook_nbval` to verify the notebook content
    hasn't changed.

    ## Coverage
    This test is intended to be used with coverage.py

    To use:
    - Set the COVERAGE_PROCESS_START environment variable to the .coveragerc file.
    - Setup .coveragerc file, see below
    - `coverage combine` the results when done
    - run pytest with `--coverage` (see conftest.py to setup parameter)

    ## .coveragerc:
    ```
    [run]
    relative_files = true: [Optional] for `python-coverage-comment-action` workflow
    parallel = true: Captures from separate threads
    omit = */*ipykernel*/*: Omits the runtime Notebook code itself

    ## Usage
    - `coverage erase`: removes previous runs
    - `coverage run -m pytest`: Runs the test cases
    - `coverage combine`: combines the coverage outputs into a single coverage file
    - `coverage report -m`: generates the report

    ## More Info on Parallel coverage.py
    - https://coverage.readthedocs.io/en/7.5.0/subprocess.html

    Args:
        notebook (Path): filename - just the filename, resolved within nb dir
    """
    with notebook.open() as f:
        nb = nbformat.read(f, as_version=4)

    coverage_env = os.environ["COVERAGE_PROCESS_START"]
    logger.debug(f"Instrumenting {f} for coverage")
    if coverage_env:
        coverage_cell = f"""
        import os
        import coverage
        if not os.environ["COVERAGE_PROCESS_START"]:
            os.environ["COVERAGE_PROCESS_START"] = r'{coverage_env}'
        coverage.process_startup()
        """
        nb.cells.insert(0, nbformat.v4.new_code_cell(coverage_cell))

    # .coveragerc must set `parallel=true`
    # https://coverage.readthedocs.io/en/7.5.0/subprocess.html

    ep = ExecutePreprocessor(timeout=NOTEBOOK_TIMEOUT)
    ep.preprocess(nb)

    # Optional: could use a nbconvert Exporter to render the notebook to HTML
    # and perform additional tests
