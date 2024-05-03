# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------ | -------: | -------: | ------: | --------: |
| nbappinator/\_\_init\_\_.py   |        3 |        0 |    100% |           |
| nbappinator/aggridhelper.py   |       10 |        5 |     50% |     22-40 |
| nbappinator/appinator.py      |      296 |      203 |     31% |47, 64-71, 80-82, 89-91, 104-107, 121-122, 139-147, 154-158, 170-171, 180-181, 193-197, 211-219, 235-239, 258-300, 329-370, 392-427, 455-463, 466, 469-476, 479, 489-528, 531-535, 538-541, 544, 547-551, 554, 557-558, 561-565, 568, 571, 585-636, 641-656, 659-670, 673-674, 679-685, 689-696, 699-700, 752, 763 |
| nbappinator/browser\_title.py |        8 |        3 |     62% |   6-7, 10 |
| nbappinator/datagrid.py       |      115 |       88 |     23% |24-30, 39-172, 202-396, 399-421, 428, 431-435 |
| nbappinator/plotly\_charts.py |       36 |       24 |     33% |15-16, 26-57 |
| nbappinator/treew.py          |       61 |       52 |     15% |10-12, 16-62, 66-69, 75-92 |
| tests/conftest.py             |        0 |        0 |    100% |           |
| tests/test\_nb.py             |       14 |        0 |    100% |           |
|                     **TOTAL** |  **543** |  **375** | **31%** |           |


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