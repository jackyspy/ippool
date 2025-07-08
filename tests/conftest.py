import pytest


def pytest_runtest_setup(item):
    if "benchmark" in item.fixturenames and not item.config.getoption(
            "--benchmark-only", False):
        pytest.skip("Benchmark tests are only run with --benchmark-only")
