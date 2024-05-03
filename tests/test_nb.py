import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import pytest
import nbappinator  # type: ignore # for coverage   # noqa: F401

notebook_dir = "notebooks"
skip_notebooks = []


@pytest.mark.parametrize(
    "notebook",
    [
        f
        for f in os.listdir(notebook_dir)
        if f.endswith(".ipynb") and f not in skip_notebooks
    ],
)
def test_notebook(notebook):
    print(f"Testing {notebook}")
    with open(os.path.join(notebook_dir, notebook)) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
    ep.preprocess(nb)
