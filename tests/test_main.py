from ums import main


def test_main_function_exists():
    assert callable(main.main)


def test_main_has_logger():
    assert hasattr(main, "logger")
