set COVERAGE_PROCESS_START=%cd%\.coveragerc

echo COVERAGE_PROCESS_START=%COVERAGE_PROCESS_START%
coverage erase
pytest --cov=nbappinator -n auto

rem coverage combine Not needed when running a single pytest-cov run
coverage report -m