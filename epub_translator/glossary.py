"""Utilities for preserving words that should not be translated."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Pattern


_DEFAULT_PRESERVE_TERMS = [
    # Common animal names
    "dragon",
    "phoenix",
    "griffin",
    "unicorn",
    "hydra",
    "pegasus",
    "wolf",
    "fox",
    "cat",
    "dog",
    "lion",
    "tiger",
    "leopard",
    "eagle",
    "falcon",
    "hawk",
    "serpent",
    "wyvern",
    # Unique artefacts or terms often left untranslated
    "mana",
    "chakra",
    "katana",
    "shuriken",
    "kunai",
    "ki",
    "dojo",
    "samurai",
    "ronin",
    "ninja",
]


@dataclass
class ProtectedText:
    text: str
    placeholders: Dict[str, str]


class GlossaryPreserver:
    """Replace glossary terms with placeholders before translation.

    This helper temporarily swaps protected terms with unique placeholders,
    allowing machine translation models to keep them intact. After translation
    the placeholders can be restored to the original words.
    """

    def __init__(self, terms: Iterable[str] | None = None) -> None:
        unique_terms = sorted({term.strip() for term in (terms or []) if term.strip()}, key=len, reverse=True)
        self._terms = unique_terms
        self._pattern: Pattern[str] | None = (
            re.compile(r"\b(" + "|".join(map(re.escape, unique_terms)) + r")\b", re.IGNORECASE)
            if unique_terms
            else None
        )

    @classmethod
    def with_defaults(cls, extra_terms: Iterable[str] | None = None) -> "GlossaryPreserver":
        terms = list(_DEFAULT_PRESERVE_TERMS)
        if extra_terms:
            terms.extend(extra_terms)
        return cls(terms)

    def protect(self, text: str) -> ProtectedText:
        if not self._pattern:
            return ProtectedText(text=text, placeholders={})

        placeholders: Dict[str, str] = {}

        def _replace(match: re.Match[str]) -> str:
            placeholder = f"⟦GLOSSARY_{len(placeholders)}⟧"
            placeholders[placeholder] = match.group(0)
            return placeholder

        protected = self._pattern.sub(_replace, text)
        return ProtectedText(text=protected, placeholders=placeholders)

    def restore(self, text: str, placeholders: Dict[str, str]) -> str:
        restored = text
        for placeholder, original in placeholders.items():
            restored = restored.replace(placeholder, original)
        return restored

    @property
    def terms(self) -> List[str]:
        return list(self._terms)


__all__ = [
    "GlossaryPreserver",
    "ProtectedText",
    "_DEFAULT_PRESERVE_TERMS",
]
