import pytest


def pytest_addoption(parser):
    parser.addoption("--coverage", action="store_true", help="Enable coverage check")


# When using pytest-xdist, make sure coverage is enabled on all tests
@pytest.fixture(scope="session", autouse=True)
def conditionally_run(pytestconfig):
    if pytestconfig.getoption("coverage"):
        import coverage

        coverage.process_startup()
