from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict


@dataclass
class SlidingWindowRateLimiter:
    max_requests: int
    window_seconds: int
    _events: Dict[str, Deque[float]] = field(default_factory=dict)

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        q = self._events.setdefault(key, deque())

        while q and q[0] < window_start:
            q.popleft()

        if len(q) >= self.max_requests:
            return False

        q.append(now)
        return True
