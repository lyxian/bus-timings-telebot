def pytest_addoption(parser):
    parser.addoption("--print", action="store_true", help="run all combinations")

def pytest_generate_tests(metafunc):
    if "verbose" in metafunc.fixturenames:
        if metafunc.config.getoption("print"):
            metafunc.parametrize("verbose", [True])