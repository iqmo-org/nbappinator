# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------ | -------: | -------: | ------: | --------: |
| nbappinator/\_\_init\_\_.py   |        3 |        0 |    100% |           |
| nbappinator/aggridhelper.py   |       10 |        0 |    100% |           |
| nbappinator/appinator.py      |      293 |       50 |     83% |270, 421, 423, 428, 438, 462-465, 472-477, 495, 501-505, 511-512, 598-614, 617-628, 631-632, 637-643, 710 |
| nbappinator/browser\_title.py |        8 |        0 |    100% |           |
| nbappinator/datagrid.py       |      115 |       40 |     65% |25, 30, 45-46, 49, 101-140, 171, 208, 210, 224, 228, 267-268, 390-394, 399-421, 431-435 |
| nbappinator/plotly\_charts.py |       34 |        3 |     91% |     46-49 |
| nbappinator/treew.py          |       61 |       26 |     57% |10-12, 37, 45-48, 51-54, 66-69, 75-92 |
| tests/conftest.py             |        0 |        0 |    100% |           |
|                     **TOTAL** |  **524** |  **119** | **77%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/iqmo-org/nbappinator/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fiqmo-org%2Fnbappinator%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.