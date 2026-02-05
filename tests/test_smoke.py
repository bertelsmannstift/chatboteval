"""Smoke tests."""


def test_package_importable() -> None:
    """Smoke test: the installed package can be imported."""
    import chatboteval

    assert chatboteval is not None
