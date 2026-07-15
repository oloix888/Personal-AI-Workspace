from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path


class CapabilityState(StrEnum):
    AVAILABLE_READ_WRITE = "AVAILABLE_READ_WRITE"
    AVAILABLE_READ_ONLY = "AVAILABLE_READ_ONLY"
    UNAVAILABLE = "UNAVAILABLE"
    UNAUTHORIZED = "UNAUTHORIZED"
    ACCOUNT_MISMATCH = "ACCOUNT_MISMATCH"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CapabilityResult:
    capability: str
    state: CapabilityState
    detail: str


@dataclass(frozen=True, slots=True)
class CompatibilityManifest:
    skill_pack_version: str
    supported_framework_versions: tuple[str, ...]
    target_framework_version: str
    minimum_contract_version: str


def load_compatibility(path: Path) -> CompatibilityManifest:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return CompatibilityManifest(
        skill_pack_version=str(payload["skill_pack_version"]),
        supported_framework_versions=tuple(payload["supported_framework_versions"]),
        target_framework_version=str(payload["target_framework_version"]),
        minimum_contract_version=str(payload["minimum_contract_version"]),
    )
