"""Round-trip and edge case tests for csv_io helpers."""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from chatboteval.core.schemas import (
    GenerationAnnotation,
    GroundingAnnotation,
    RetrievalAnnotation,
    Task,
    read_csv,
    write_csv,
)

_DT = datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def retrieval(language: str | None = None) -> RetrievalAnnotation:
    return RetrievalAnnotation(
        record_uuid="r-001",
        annotator_id="ann-1",
        task=Task.RETRIEVAL,
        language=language,
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        input_query="What is X?",
        chunk="X is Y.",
        chunk_id="c-1",
        doc_id="d-1",
        chunk_rank=1,
        topically_relevant=True,
        evidence_sufficient=False,
        misleading=False,
        notes="",
    )


@pytest.fixture
def retrieval_no_lang() -> RetrievalAnnotation:
    return RetrievalAnnotation(
        record_uuid="r-002",
        annotator_id="ann-2",
        task=Task.RETRIEVAL,
        language=None,
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        input_query="Query?",
        chunk="Chunk text.",
        chunk_id="c-2",
        doc_id="d-2",
        chunk_rank=3,
        topically_relevant=False,
        evidence_sufficient=True,
        misleading=True,
        notes="some note",
    )


@pytest.fixture
def grounding() -> GroundingAnnotation:
    return GroundingAnnotation(
        record_uuid="g-001",
        annotator_id="ann-3",
        task=Task.GROUNDING,
        language="de",
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        answer="The answer is A.",
        context_set="ctx text",
        support_present=True,
        unsupported_claim_present=False,
        contradicted_claim_present=False,
        source_cited=True,
        fabricated_source=False,
        notes="",
    )


@pytest.fixture
def generation() -> GenerationAnnotation:
    return GenerationAnnotation(
        record_uuid="gen-001",
        annotator_id="ann-4",
        task=Task.GENERATION,
        language="en",
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        query="Explain Z.",
        answer="Z is...",
        proper_action=True,
        response_on_topic=True,
        helpful=True,
        incomplete=False,
        unsafe_content=False,
        notes="",
    )


# --- write_csv: empty list is no-op ---


def test_write_csv_empty_no_file(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    write_csv([], out)
    assert not out.exists()


# --- write_csv: boolean values are lowercase ---


def test_write_csv_booleans_lowercase(tmp_path: Path, retrieval_no_lang: RetrievalAnnotation) -> None:
    out = tmp_path / "ret.csv"
    write_csv([retrieval_no_lang], out)
    content = out.read_text()
    assert "true" in content or "false" in content
    assert "True" not in content
    assert "False" not in content


# --- write_csv: None written as empty string ---


def test_write_csv_none_as_empty_string(tmp_path: Path, retrieval_no_lang: RetrievalAnnotation) -> None:
    out = tmp_path / "ret.csv"
    write_csv([retrieval_no_lang], out)
    import csv

    with out.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["language"] == ""


# --- write_csv: enum written as string value ---


def test_write_csv_task_enum_as_string(tmp_path: Path, grounding: GroundingAnnotation) -> None:
    out = tmp_path / "grnd.csv"
    write_csv([grounding], out)
    import csv

    with out.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["task"] == "grounding"


# --- Round-trips ---


def test_roundtrip_retrieval_with_language(tmp_path: Path) -> None:
    rec = RetrievalAnnotation(
        record_uuid="r-rt",
        annotator_id="ann-rt",
        task=Task.RETRIEVAL,
        language="en",
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        input_query="Q?",
        chunk="C.",
        chunk_id="c-rt",
        doc_id="d-rt",
        chunk_rank=2,
        topically_relevant=True,
        evidence_sufficient=True,
        misleading=False,
        notes="",
    )
    out = tmp_path / "ret_lang.csv"
    write_csv([rec], out)
    result = read_csv(out, RetrievalAnnotation)
    assert result == [rec]


def test_roundtrip_retrieval_language_none(tmp_path: Path, retrieval_no_lang: RetrievalAnnotation) -> None:
    """Critical edge case: language=None must survive CSV round-trip."""
    out = tmp_path / "ret_none.csv"
    write_csv([retrieval_no_lang], out)
    result = read_csv(out, RetrievalAnnotation)
    assert result == [retrieval_no_lang]
    assert result[0].language is None


def test_roundtrip_grounding(tmp_path: Path, grounding: GroundingAnnotation) -> None:
    out = tmp_path / "grnd.csv"
    write_csv([grounding], out)
    result = read_csv(out, GroundingAnnotation)
    assert result == [grounding]


def test_roundtrip_generation(tmp_path: Path, generation: GenerationAnnotation) -> None:
    out = tmp_path / "gen.csv"
    write_csv([generation], out)
    result = read_csv(out, GenerationAnnotation)
    assert result == [generation]


def test_roundtrip_multiple_rows(
    tmp_path: Path, retrieval_no_lang: RetrievalAnnotation, grounding: GroundingAnnotation
) -> None:
    r1 = RetrievalAnnotation(
        record_uuid="multi-1",
        annotator_id="ann-a",
        task=Task.RETRIEVAL,
        language="en",
        inserted_at=_DT,
        created_at=_DT,
        record_status="submitted",
        input_query="Q1",
        chunk="C1",
        chunk_id="c-m1",
        doc_id="d-m1",
        chunk_rank=1,
        topically_relevant=True,
        evidence_sufficient=False,
        misleading=False,
        notes="",
    )
    r2 = retrieval_no_lang
    out = tmp_path / "multi.csv"
    write_csv([r1, r2], out)
    result = read_csv(out, RetrievalAnnotation)
    assert result == [r1, r2]


# --- read_csv: extra columns fail validation ---


def test_read_csv_extra_column_raises(tmp_path: Path, grounding: GroundingAnnotation) -> None:
    import csv

    out = tmp_path / "grnd.csv"
    write_csv([grounding], out)
    # Append an extra column
    with out.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or []) + ["extra_col"]
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row["extra_col"] = "oops"
            writer.writerow(row)
    with pytest.raises(ValidationError):
        read_csv(out, GroundingAnnotation)
