"""Operational settings for annotation setup (workspace topology, distribution)."""

from dataclasses import dataclass, field
from typing import Literal

from chatboteval.core.schemas.annotation_task import Task
from chatboteval.core.settings.settings_base import ResolveSettings


class AnnotationSetupSettings(ResolveSettings):
    """Configurable runtime settings for annotation setup.

    Controls workspace topology and task-distribution thresholds.
    Schema definitions (rg.Settings per task) are hardcoded — see schemas.py.
    """

    workspace_prefix: str = ""
    workspace_dataset_map: dict[str, list[Task]] = {
        "retrieval_grounding": [Task.RETRIEVAL, Task.GROUNDING],
        "generation": [Task.GENERATION],
    }
    min_submitted: int = 1


@dataclass
class UserSpec:
    """Specification for provisioning an Argilla user account."""

    username: str
    role: Literal["owner", "annotator"]
    workspaces: list[str] = field(default_factory=list)
    password: str | None = None
