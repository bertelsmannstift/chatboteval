"""Tests for base contract types."""

import pytest
from pydantic import ValidationError

from chatboteval.core.schemas.base import ContractModel, Task


class _Simple(ContractModel):
    """Minimal ContractModel subclass for testing."""

    x: int


def test_task_values():
    """Task enum members have expected string values."""
    assert Task.RETRIEVAL == "retrieval"
    assert Task.GROUNDING == "grounding"
    assert Task.GENERATION == "generation"


def test_task_from_string():
    """Task can be constructed from its string value."""
    assert Task("retrieval") is Task.RETRIEVAL


def test_task_invalid_raises():
    """Invalid string raises ValueError."""
    with pytest.raises(ValueError):
        Task("invalid")


def test_task_has_three_members():
    """Task enum has exactly three members."""
    assert len(list(Task)) == 3


def test_contract_model_frozen():
    """ContractModel instances are immutable."""
    m = _Simple(x=1)
    with pytest.raises(ValidationError):
        m.x = 2


def test_contract_model_extra_forbidden():
    """ContractModel rejects extra fields."""
    with pytest.raises(ValidationError):
        _Simple(x=1, y=99)
