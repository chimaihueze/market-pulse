import random

from app.config.settings import settings


class Backoff:
    def __init__(self, base=settings.backoff_base, cap=settings.backoff_cap):
        self.base = base
        self.cap = cap
        self.attempt = 0

    def next_delay(self) -> float:
        exp = float(min(self.cap, self.base * (2 ** self.attempt)))
        jitter = exp * 0.2 * random.random()
        return exp + jitter

    def success(self):
        self.attempt = max(0, self.attempt - 1)

    def failure(self):
        self.attempt += 1
