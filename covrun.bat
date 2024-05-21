set COVERAGE_PROCESS_START=%cd%\.coveragerc

echo COVERAGE_PROCESS_START=%COVERAGE_PROCESS_START%
coverage erase
pytest --cov=nbappinator -n 10 --coverage
coverage combine
coverage report -m