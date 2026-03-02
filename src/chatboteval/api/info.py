"""Version resolution utilities for chatboteval."""

from importlib import metadata

__all__ = ["get_version"]


def get_version(dist_name: str = "chatboteval") -> str:
    """Return installed distribution version."""
    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "0.0.0"
