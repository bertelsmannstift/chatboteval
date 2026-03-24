"""Pytest configuration for unit/api tests.

Module-level patch — build_task_settings() is called at collection time.
"""

from unittest.mock import MagicMock

import argilla as rg

if rg.Argilla._default_client is None:
    rg.Argilla._default_client = MagicMock()
