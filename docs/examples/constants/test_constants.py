from . import main


def test_main(monkeypatch):
    """Ensure the injected result matches what is expected."""
    # Put a config value in the environ and get from there.
    monkeypatch.setenv("PUNCTUATION", "!!!")
    assert main() == "Hello!!!"
