from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple


DEFAULT_SEED = 20260706
DEFAULT_REPEATS = 3
DEFAULT_WARMUPS = 1
DEFAULT_FORMATS = ("json", "csv", "md")


@dataclass(frozen=True)
class BenchmarkConfig:
    repeats: int = DEFAULT_REPEATS
    warmups: int = DEFAULT_WARMUPS
    seed: int = DEFAULT_SEED
    output_dir: Path = Path("reports")
    formats: Tuple[str, ...] = DEFAULT_FORMATS

    def __post_init__(self) -> None:
        if self.repeats <= 0:
            raise ValueError("repeats must be positive")
        if self.warmups < 0:
            raise ValueError("warmups cannot be negative")
        if not self.formats:
            raise ValueError("at least one output format is required")
        unsupported = set(self.formats).difference({"json", "csv", "md"})
        if unsupported:
            raise ValueError(f"unsupported report formats: {', '.join(sorted(unsupported))}")

    @classmethod
    def from_values(
        cls,
        repeats: int = DEFAULT_REPEATS,
        warmups: int = DEFAULT_WARMUPS,
        seed: int = DEFAULT_SEED,
        output_dir: str | Path = "reports",
        formats: str | Iterable[str] = DEFAULT_FORMATS,
    ) -> "BenchmarkConfig":
        if isinstance(formats, str):
            normalized = tuple(item.strip() for item in formats.split(",") if item.strip())
        else:
            normalized = tuple(formats)
        return cls(
            repeats=repeats,
            warmups=warmups,
            seed=seed,
            output_dir=Path(output_dir),
            formats=normalized,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "repeats": self.repeats,
            "warmups": self.warmups,
            "seed": self.seed,
            "output_dir": str(self.output_dir),
            "formats": list(self.formats),
        }
