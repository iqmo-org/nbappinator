import pytest
import nbformat

from pathlib import Path
from nbconvert.preprocessors import ExecutePreprocessor
from .env_helper import NOTEBOOK_DIR, SEARCH, SKIP_NOTEBOOKS, NOTEBOOK_TIMEOUT


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

    This test is a low standard: it doesn't verify the notebooks are usable. It's useful with coverage.py to verify that your notebooks execute
    all the code paths.

    To make this method more robust, add assertions to the end of your notebooks `assert xyz`.

    Or, alternatively, use `test_notebook_nbval` to verify the notebook content hasn't changed.

    ## Coverage
    This test is intended to be used with coverage.py

    To use:
    - Set the COVERAGE_PROCESS_START environment variable to the location of your .coveragerc file.
    - Setup your .coveragerc file, see below
    - `coverage combine` the results when done
    - run pytest with `--coverage` (see conftest.py to setup parameter)

    ## .coveragerc:
    ```
    [run]
    relative_files = true  # needed for `python-coverage-comment-action` in our github action. Optional.
    parallel = true  # required because each Notebook runs in a separate thread
    omit = */*ipykernel*/*  # required to exclude the Notebook code itself from the coverage check and coverage will complain about not finding the code.

    ## Usage
    - `coverage erase`: removes previous runs
    - `coverage run -m pytest`: Runs the test cases
    - `coverage combine`: combines the coverage outputs into a single coverage file
    - `coverage report -m`: generates the report

    ## More Info on Parallel coverage.py
    - https://coverage.readthedocs.io/en/7.5.0/subprocess.html

    Args:
        notebook (Path): filename - just the filename, it will be resolved within the notebook_dir
    """
    with open(notebook) as f:
        nb = nbformat.read(f, as_version=4)

    coverage = pytestconfig.getoption("coverage")
    if coverage:
        nb.cells.insert(
            0, nbformat.v4.new_code_cell("import coverage\ncoverage.process_startup()")
        )

    # This requires COVERAGE_PROCESS_START environment variable
    # and parallel=true
    # and omit the generated .py code
    # https://coverage.readthedocs.io/en/7.5.0/subprocess.html

    ep = ExecutePreprocessor(timeout=NOTEBOOK_TIMEOUT)
    ep.preprocess(nb)
