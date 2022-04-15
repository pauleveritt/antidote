"""A library or framework in another, foreign package."""

from dataclasses import dataclass


@dataclass
class Greeting:
    punctuation: str
    salutation: str = "Hello"

