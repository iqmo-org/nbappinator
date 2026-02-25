# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/iqmo-org/nbappinator/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------ | -------: | -------: | ------: | --------: |
| nbappinator/\_\_init\_\_.py   |        7 |        0 |    100% |           |
| nbappinator/\_version.py      |        1 |        0 |    100% |           |
| nbappinator/aggridhelper.py   |       14 |        2 |     86% |    24, 26 |
| nbappinator/app.py            |      240 |       29 |     88% |165, 179, 261-264, 557-561, 573, 579, 588, 592-596, 605, 618-620, 638-640, 651-653, 659 |
| nbappinator/browser\_title.py |        8 |        0 |    100% |           |
| nbappinator/datagrid.py       |      114 |        0 |    100% |           |
| nbappinator/graphvizgraph.py  |       59 |       10 |     83% |272-273, 282-283, 294-296, 309, 313, 319-321 |
| nbappinator/jinjamagic.py     |        0 |        0 |    100% |           |
| nbappinator/networkgraph.py   |       22 |        0 |    100% |           |
| nbappinator/plotly\_charts.py |       30 |        2 |     93% |     16-17 |
| nbappinator/treew.py          |       46 |        2 |     96% |  266, 282 |
|                     **TOTAL** |  **541** |   **45** | **92%** |           |


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