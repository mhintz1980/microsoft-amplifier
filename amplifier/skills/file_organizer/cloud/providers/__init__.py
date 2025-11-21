"""
Cloud provider implementations.

This package contains provider-specific implementations for different
cloud storage services, all conforming to the BaseProvider interface.
"""

from .base_provider import BaseProvider
from .local_provider import LocalProvider

# Import actual cloud providers when implemented
# from .onedrive_provider import OneDriveProvider
# from .gdrive_provider import GDriveProvider
# from .dropbox_provider import DropboxProvider

__all__ = [
    "BaseProvider",
    "LocalProvider",
    # "OneDriveProvider",
    # "GDriveProvider",
    # "DropboxProvider",
]


def get_provider(provider_type: str):
    """
    Factory function to get the appropriate provider instance.

    Args:
        provider_type: Type of provider ("onedrive", "gdrive", "dropbox", "local")

    Returns:
        Provider instance of the requested type

    Raises:
        ValueError: If provider type is not supported
    """
    provider_map = {
        "local": LocalProvider,
        # "onedrive": OneDriveProvider,
        # "gdrive": GDriveProvider,
        # "dropbox": DropboxProvider,
    }

    if provider_type not in provider_map:
        raise ValueError(f"Unsupported provider type: {provider_type}")

    return provider_map[provider_type]
