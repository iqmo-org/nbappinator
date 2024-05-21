def pytest_addoption(parser):
    parser.addoption("--coverage", action="store_true", help="Enable coverage check")
