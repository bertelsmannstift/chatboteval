"""Integration tests for the public synthetic query generation surface."""

from pathlib import Path

import pytest

from pragmata import querygen
from pragmata.core.settings.settings_base import MissingSecretError

pytestmark = [pytest.mark.integration, pytest.mark.querygen]


def _choice_values(items: object) -> list[str]:
    """Extract raw values from a canonicalized weighted-choice list."""
    return [item.value for item in items]  # type: ignore[attr-defined]


def _domains_from_spec(spec: object) -> list[str]:
    """Return resolved domain values across flat or nested spec variants."""
    if hasattr(spec, "domain_context"):
        return _choice_values(spec.domain_context.domains)  # type: ignore[attr-defined]
    return _choice_values(spec.domains)  # type: ignore[attr-defined]


def test_gen_queries_prepares_run_via_public_surface(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Prepare a synthetic query generation run through the public surface."""
    monkeypatch.setenv("MISTRAL_API_KEY", "test-mistral-api-key")

    base_dir = tmp_path / "workspace"
    run_id = "integration-run-001"

    result = querygen.gen_queries(
        domains="healthcare",
        roles=["patient", "caregiver"],
        languages="en",
        topics="insurance coverage",
        intents="understand benefits",
        tasks="factual lookup",
        difficulty="basic",
        formats="bullet list",
        disallowed_topics=["medical diagnosis"],
        base_dir=base_dir,
        run_id=run_id,
        n_queries=3,
        model_provider="mistralai",
        planning_model="magistral-medium-latest",
        realization_model="mistral-medium-latest",
    )

    expected_run_dir = base_dir.resolve() / "querygen" / "runs" / run_id

    assert isinstance(result, querygen.QueryGenRunResult)

    assert result.settings.run_id == run_id
    assert result.settings.n_queries == 3
    assert result.settings.base_dir == base_dir
    assert result.settings.llm.model_provider == "mistralai"
    assert result.settings.llm.planning_model == "magistral-medium-latest"
    assert result.settings.llm.realization_model == "mistral-medium-latest"

    assert _domains_from_spec(result.settings.spec) == ["healthcare"]

    assert result.paths.run_dir == expected_run_dir
    assert result.paths.synthetic_queries_csv == expected_run_dir / "synthetic_queries.csv"
    assert result.paths.synthetic_queries_meta_json == expected_run_dir / "synthetic_queries.meta.json"

    assert result.paths.run_dir.exists()
    assert result.paths.run_dir.is_dir()
    assert not result.paths.synthetic_queries_csv.exists()
    assert not result.paths.synthetic_queries_meta_json.exists()


def test_gen_queries_raises_when_provider_api_key_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Fail with the expected missing-secret error when the provider key is absent."""
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)

    base_dir = tmp_path / "workspace"
    run_id = "integration-run-missing-secret"
    expected_run_dir = base_dir.resolve() / "querygen" / "runs" / run_id

    with pytest.raises(MissingSecretError, match="MISTRAL_API_KEY"):
        querygen.gen_queries(
            domains="healthcare",
            roles="patient",
            languages="en",
            topics="insurance coverage",
            intents="understand benefits",
            tasks="factual lookup",
            base_dir=base_dir,
            run_id=run_id,
            n_queries=2,
            model_provider="mistralai",
        )

    assert not expected_run_dir.exists()