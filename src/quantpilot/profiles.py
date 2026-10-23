"""Operating policy, independent of execution transport and position sizing."""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Self

from pydantic import Field, model_validator

from quantpilot.models import DomainModel


class OperatingProfile(str, Enum):
    CONTINUOUS = "CONTINUOUS"
    COMPETITION = "COMPETITION"


class ProfileConfig(DomainModel):
    operating_profile: OperatingProfile = OperatingProfile.CONTINUOUS
    starts_at: datetime | None = None
    deadline: datetime | None = None
    entry_cutoff: datetime | None = None
    force_final_liquidation: bool = False
    liquidation_seconds: int = Field(default=300, ge=1)

    @model_validator(mode="before")
    @classmethod
    def legacy_deadline(cls, value: Any) -> Any:
        # Old deadline-bearing configs explicitly requested competition behavior.
        if isinstance(value, dict) and "operating_profile" not in value and value.get("deadline"):
            value = dict(value)
            value["operating_profile"] = OperatingProfile.COMPETITION
            value.setdefault("force_final_liquidation", True)
        return value

    @model_validator(mode="after")
    def valid_profile(self) -> Self:
        if self.operating_profile == OperatingProfile.CONTINUOUS:
            if any(
                (self.starts_at, self.deadline, self.entry_cutoff, self.force_final_liquidation)
            ):
                raise ValueError("Continuous profile cannot contain competition timing policies")
        else:
            if self.starts_at and self.deadline and self.starts_at >= self.deadline:
                raise ValueError("Competition start must precede deadline")
            if self.entry_cutoff and self.deadline and self.entry_cutoff > self.deadline:
                raise ValueError("Entry cutoff must not exceed deadline")
        return self

    def expired(self, now: datetime) -> bool:
        return self.deadline is not None and now >= self.deadline

    def settling(self, now: datetime, terminal: datetime | None = None) -> bool:
        end = self.deadline or terminal
        return (
            self.operating_profile == OperatingProfile.COMPETITION
            and self.force_final_liquidation
            and end is not None
            and now >= end - timedelta(seconds=self.liquidation_seconds)
        )

    def entries_allowed(self, now: datetime, terminal: datetime | None = None) -> bool:
        return not (
            (self.starts_at is not None and now < self.starts_at)
            or self.expired(now)
            or (self.entry_cutoff is not None and now >= self.entry_cutoff)
            or self.settling(now, terminal)
        )
