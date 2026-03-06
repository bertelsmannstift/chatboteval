import pytest
from pydantic import ValidationError

from chatboteval.core.schemas.annotation_import import Chunk, QueryResponsePair


@pytest.fixture()
def valid_chunk():
    return {"chunk_id": "c1", "doc_id": "d1", "chunk_rank": 1, "text": "Some text."}


@pytest.fixture()
def valid_qrp(valid_chunk):
    return {
        "query": "What is X?",
        "answer": "X is Y.",
        "chunks": [valid_chunk],
        "context_set": "ctx-001",
        "language": "en",
    }


def test_valid_qrp_passes(valid_qrp):
    qrp = QueryResponsePair(**valid_qrp)
    assert qrp.query == "What is X?"


def test_language_none_accepted(valid_qrp):
    valid_qrp["language"] = None
    qrp = QueryResponsePair(**valid_qrp)
    assert qrp.language is None


def test_language_omitted_accepted(valid_qrp):
    del valid_qrp["language"]
    qrp = QueryResponsePair(**valid_qrp)
    assert qrp.language is None


@pytest.mark.parametrize("field", ["query", "answer", "context_set"])
def test_empty_string_rejected(valid_qrp, field):
    valid_qrp[field] = ""
    with pytest.raises(ValidationError):
        QueryResponsePair(**valid_qrp)


@pytest.mark.parametrize("field", ["query", "answer", "context_set"])
def test_whitespace_only_rejected(valid_qrp, field):
    valid_qrp[field] = "   "
    with pytest.raises(ValidationError):
        QueryResponsePair(**valid_qrp)


def test_empty_chunks_rejected(valid_qrp):
    valid_qrp["chunks"] = []
    with pytest.raises(ValidationError):
        QueryResponsePair(**valid_qrp)


def test_chunk_rank_zero_rejected(valid_chunk):
    valid_chunk["chunk_rank"] = 0
    with pytest.raises(ValidationError):
        Chunk(**valid_chunk)


@pytest.mark.parametrize("field", ["chunk_id", "doc_id", "text"])
def test_empty_chunk_string_rejected(valid_chunk, field):
    valid_chunk[field] = ""
    with pytest.raises(ValidationError):
        Chunk(**valid_chunk)


@pytest.mark.parametrize("field", ["chunk_id", "doc_id", "text"])
def test_whitespace_chunk_string_rejected(valid_chunk, field):
    valid_chunk[field] = "  "
    with pytest.raises(ValidationError):
        Chunk(**valid_chunk)


def test_extra_field_on_qrp_rejected(valid_qrp):
    valid_qrp["unknown"] = "x"
    with pytest.raises(ValidationError):
        QueryResponsePair(**valid_qrp)


def test_extra_field_on_chunk_rejected(valid_chunk):
    valid_chunk["unknown"] = "x"
    with pytest.raises(ValidationError):
        Chunk(**valid_chunk)
