"""Command line interface for translating EPUB files."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Iterable, List

from .epub_processor import EPUBTranslator
from .glossary import GlossaryPreserver
from .translator import HuggingFaceTranslator

LOGGER = logging.getLogger(__name__)


def _load_glossary_terms(files: Iterable[Path]) -> List[str]:
    terms: List[str] = []
    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        if file_path.suffix.lower() == ".json":
            data = json.loads(content)
            if isinstance(data, list):
                terms.extend(str(item) for item in data)
            else:
                raise ValueError(f"Glossary JSON must be a list of strings: {file_path}")
        else:
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    terms.append(line)
    return terms


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate EPUB files from English to Indonesian.")
    parser.add_argument("input", type=Path, help="Path to the input EPUB file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to the translated EPUB (defaults to adding .id before the extension)",
    )
    parser.add_argument(
        "--glossary",
        type=Path,
        action="append",
        default=[],
        help="Path to a text or JSON file containing terms that should not be translated",
    )
    parser.add_argument(
        "--preserve",
        action="append",
        default=[],
        help="Additional words that should be preserved (can be passed multiple times)",
    )
    parser.add_argument(
        "--model",
        default="Helsinki-NLP/opus-mt-en-id",
        help="HuggingFace model to use for translation",
    )
    parser.add_argument(
        "--no-default-glossary",
        action="store_true",
        help="Disable the built-in list of animals and unique terms to preserve",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Number of text nodes translated at once",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help="Maximum sequence length for the translation model",
    )
    parser.add_argument(
        "--device",
        default="auto",
        help="Computation device for the model (cpu, cuda, atau auto)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser


def main(args: list[str] | None = None) -> int:
    parser = build_parser()
    namespace = parser.parse_args(args=args)

    logging.basicConfig(
        level=getattr(logging, namespace.log_level),
        format="%(levelname)s: %(message)s",
    )

    input_path: Path = namespace.input
    if not input_path.exists():
        parser.error(f"Input file does not exist: {input_path}")

    output_path: Path
    if namespace.output:
        output_path = namespace.output
    else:
        if input_path.suffix.lower() == ".epub":
            stem = input_path.stem + ".id"
            output_path = input_path.with_name(f"{stem}.epub")
        else:
            output_path = input_path.with_name(input_path.name + ".id.epub")

    glossary_files: List[Path] = [Path(path) for path in namespace.glossary]
    preserve_terms = list(namespace.preserve or [])
    if glossary_files:
        preserve_terms.extend(_load_glossary_terms(glossary_files))

    if namespace.no_default_glossary:
        glossary = GlossaryPreserver(preserve_terms)
    else:
        glossary = GlossaryPreserver.with_defaults(preserve_terms)

    device = None if namespace.device.lower() == "auto" else namespace.device

    translator = HuggingFaceTranslator(
        model_name=namespace.model,
        max_length=namespace.max_length,
        device=device,
    )
    processor = EPUBTranslator(translator=translator, glossary=glossary, batch_size=namespace.batch_size)

    LOGGER.info("Translating %s to %s", input_path, output_path)
    processor.translate_book(input_path=input_path, output_path=output_path)
    LOGGER.info("Translation finished")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
