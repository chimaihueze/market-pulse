from typing import Generic, TypeVar

T = TypeVar("T")

class Result(Generic[T]):
    def __init__(self, ok: bool, value: T | None = None, error: str | None = None):
        self.ok = ok
        self.value = value
        self.error = error

    @staticmethod
    def success(value: T) -> "Result[T]":
        return Result(True, value=value)

    @staticmethod
    def fail(error: str) -> "Result[T]":
        return Result(False, error=error)