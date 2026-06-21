from dataclasses import dataclass


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
