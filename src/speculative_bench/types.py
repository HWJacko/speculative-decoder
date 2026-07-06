from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping, Sequence


@dataclass(frozen=True)
class BenchmarkCase:
    """A deterministic text-generation workload definition."""

    name: str
    prompt: str
    target_tokens: int
    draft_tokens: int
    acceptance_pattern: Sequence[int]
    tags: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("benchmark case name is required")
        if not self.prompt:
            raise ValueError(f"benchmark case {self.name!r} requires a prompt")
        if self.target_tokens <= 0:
            raise ValueError(f"benchmark case {self.name!r} target_tokens must be positive")
        if self.draft_tokens < 0:
            raise ValueError(f"benchmark case {self.name!r} draft_tokens cannot be negative")
        if not self.acceptance_pattern:
            raise ValueError(f"benchmark case {self.name!r} requires an acceptance_pattern")
        if any(bit not in (0, 1) for bit in self.acceptance_pattern):
            raise ValueError(f"benchmark case {self.name!r} acceptance_pattern must contain only 0 or 1")

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "BenchmarkCase":
        return cls(
            name=str(data["name"]),
            prompt=str(data["prompt"]),
            target_tokens=int(data["target_tokens"]),
            draft_tokens=int(data.get("draft_tokens", data["target_tokens"])),
            acceptance_pattern=tuple(int(bit) for bit in data["acceptance_pattern"]),
            tags=tuple(str(tag) for tag in data.get("tags", ())),
            metadata=dict(data.get("metadata", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "target_tokens": self.target_tokens,
            "draft_tokens": self.draft_tokens,
            "acceptance_pattern": list(self.acceptance_pattern),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DecoderRun:
    algorithm: str
    case_name: str
    repetition: int
    target_tokens: int
    output_tokens: int
    draft_tokens: int
    accepted_tokens: int
    rejected_tokens: int
    model_steps: int
    elapsed_ms: float
    phase: str = "steady_state"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "case_name": self.case_name,
            "repetition": self.repetition,
            "phase": self.phase,
            "target_tokens": self.target_tokens,
            "output_tokens": self.output_tokens,
            "draft_tokens": self.draft_tokens,
            "accepted_tokens": self.accepted_tokens,
            "rejected_tokens": self.rejected_tokens,
            "model_steps": self.model_steps,
            "elapsed_ms": self.elapsed_ms,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class MetricRow:
    case_name: str
    algorithm: str
    repetitions: int
    mean_elapsed_ms: float
    stdev_elapsed_ms: float
    tokens_per_second: float
    acceptance_rate: float
    draft_efficiency: float
    model_steps_mean: float
    speedup_vs_baseline: float | None
    model_step_reduction_vs_baseline: float | None
    confidence_note: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkResult:
    generated_at: str
    environment: Mapping[str, Any]
    config: Mapping[str, Any]
    cases: List[Dict[str, Any]]
    cold_start_ms: Mapping[str, float]
    rows: List[MetricRow]
    runs: List[DecoderRun]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "environment": dict(self.environment),
            "config": dict(self.config),
            "cases": self.cases,
            "cold_start_ms": dict(self.cold_start_ms),
            "rows": [row.to_dict() for row in self.rows],
            "runs": [run.to_dict() for run in self.runs],
        }
