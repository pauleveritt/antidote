from . import main


def test_main():
    assert main() == (
        'Bonjour, my name is Marie!',
        'Hello, my name is Fred!'
    )
