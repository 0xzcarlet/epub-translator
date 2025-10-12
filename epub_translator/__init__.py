"""epub_translator package."""
from __future__ import annotations

from typing import Sequence


def main(args: Sequence[str] | None = None) -> int:
    from .cli import main as cli_main

    return cli_main(list(args) if args is not None else None)


__all__ = ["main"]
