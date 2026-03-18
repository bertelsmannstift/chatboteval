"""Version resolution utilities for pragmata."""

from importlib import metadata


def get_version(dist_name: str = "pragmata") -> str:
    """Return installed distribution version."""
    return metadata.version(dist_name)
