coverage erase
coverage run -m pytest -n 10 --coverage
rem disabled because of inconsistent results
rem pytest --cov=nbappinator -n 10
coverage combine
coverage report -m