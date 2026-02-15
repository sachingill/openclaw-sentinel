from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


class CronParseError(ValueError):
    pass


def _parse_field(field: str, minimum: int, maximum: int) -> set[int]:
    field = field.strip()
    if field == "*":
        return set(range(minimum, maximum + 1))

    values: set[int] = set()
    for part in field.split(","):
        part = part.strip()
        if not part:
            raise CronParseError("empty cron segment")

        if part.startswith("*/"):
            step = int(part[2:])
            if step <= 0:
                raise CronParseError("cron step must be > 0")
            values.update(range(minimum, maximum + 1, step))
            continue

        if "-" in part:
            start_raw, end_raw = part.split("-", 1)
            start = int(start_raw)
            end = int(end_raw)
            if start > end:
                raise CronParseError("cron range start must be <= end")
            if start < minimum or end > maximum:
                raise CronParseError("cron range out of bounds")
            values.update(range(start, end + 1))
            continue

        value = int(part)
        if value < minimum or value > maximum:
            raise CronParseError("cron value out of bounds")
        values.add(value)

    return values


@dataclass(frozen=True)
class CronSchedule:
    minute: set[int]
    hour: set[int]
    day: set[int]
    month: set[int]
    weekday: set[int]

    @classmethod
    def parse(cls, expression: str) -> "CronSchedule":
        parts = expression.split()
        if len(parts) != 5:
            raise CronParseError("cron expression must contain 5 fields")

        minute = _parse_field(parts[0], 0, 59)
        hour = _parse_field(parts[1], 0, 23)
        day = _parse_field(parts[2], 1, 31)
        month = _parse_field(parts[3], 1, 12)
        # Normalize weekday to Python datetime.weekday convention (Mon=0..Sun=6).
        raw_weekday = _parse_field(parts[4], 0, 6)
        weekday = {(d - 1) % 7 for d in raw_weekday}

        return cls(minute=minute, hour=hour, day=day, month=month, weekday=weekday)

    def matches(self, dt: datetime) -> bool:
        return (
            dt.minute in self.minute
            and dt.hour in self.hour
            and dt.day in self.day
            and dt.month in self.month
            and dt.weekday() in self.weekday
        )

    def next_after(self, dt: datetime) -> datetime:
        candidate = dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(366 * 24 * 60):
            if self.matches(candidate):
                return candidate
            candidate += timedelta(minutes=1)
        raise CronParseError("unable to find next cron execution within search window")
