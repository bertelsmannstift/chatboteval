"""Annotation import API — thin orchestration over core/ implementation.

Public API:
    validate_records(records) -> ValidationResult
    import_records(client, records, *, workspace_prefix=UNSET, ...) -> ImportResult
"""

from dataclasses import dataclass
from pathlib import Path

import argilla as rg

from pragmata.core.annotation.record_builder import fan_out_records
from pragmata.core.schemas.annotation_import import QueryResponsePair
from pragmata.core.settings.annotation_settings import AnnotationSettings
from pragmata.core.settings.settings_base import UNSET, load_config_file

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RecordError:
    """Validation failure for a single input record."""

    index: int
    detail: str


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of validate_records(): typed pairs and per-index errors."""

    valid: list[QueryResponsePair]
    errors: list[RecordError]


@dataclass(frozen=True)
class ImportResult:
    """Outcome of import_records(): counts per dataset and overall totals."""

    total_records: int
    imported_records: int
    skipped_records: int
    dataset_counts: dict[str, int]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def validate_records(records: list[dict]) -> ValidationResult:
    """Validate raw dicts against the canonical QueryResponsePair schema.

    Pure validation — no Argilla I/O. Use before import_records() to separate
    schema errors from import errors.

    Args:
        records: Raw dictionaries to validate against QueryResponsePair.

    Returns:
        ValidationResult with successfully parsed pairs and per-index errors.
    """
    valid: list[QueryResponsePair] = []
    errors: list[RecordError] = []
    for i, raw in enumerate(records):
        try:
            valid.append(QueryResponsePair.model_validate(raw))
        except Exception as exc:
            errors.append(RecordError(index=i, detail=str(exc)))
    return ValidationResult(valid=valid, errors=errors)


def import_records(
    client: rg.Argilla,
    records: list[QueryResponsePair],
    *,
    workspace_prefix: str | object = UNSET,
    config_path: str | Path | object = UNSET,
) -> ImportResult:
    """Fan out validated records to the three Argilla annotation datasets.

    Each QueryResponsePair produces records in retrieval (one per chunk),
    grounding (one per pair), and generation (one per pair) datasets.
    Record IDs are derived from content hashes for idempotent upsert.

    Datasets must already exist (call setup() first).

    Args:
        client: Connected Argilla client instance.
        records: Validated QueryResponsePair objects to import.
        workspace_prefix: Prefix used when the environment was created.
        config_path: Path to YAML config file for settings resolution.

    Returns:
        ImportResult with total/imported/skipped counts and per-dataset breakdown.
    """
    settings = AnnotationSettings.resolve(
        config=load_config_file(config_path) if config_path is not UNSET else None,
        overrides={"workspace_prefix": workspace_prefix},
    )
    dataset_counts = fan_out_records(client, records, settings)
    total = len(records)
    return ImportResult(
        total_records=total,
        imported_records=total,
        skipped_records=0,
        dataset_counts=dataset_counts,
    )
