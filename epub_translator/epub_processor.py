"""Utilities for translating EPUB files."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List, Optional

import ebooklib
from bs4 import BeautifulSoup, NavigableString
from ebooklib import epub

from .glossary import GlossaryPreserver
from .translator import HuggingFaceTranslator

LOGGER = logging.getLogger(__name__)
SKIP_TAGS = {"script", "style"}


def _get_first_metadata(book: epub.EpubBook, namespace: str, name: str) -> Optional[str]:
    try:
        entries = book.get_metadata(namespace, name)
    except AttributeError:
        return None
    if not entries:
        return None
    value, _attrs = entries[0]
    return value


def _iter_text_nodes(soup: BeautifulSoup) -> Iterable[NavigableString]:
    for element in soup.descendants:
        if isinstance(element, NavigableString):
            parent = element.parent
            if parent and parent.name and parent.name.lower() in SKIP_TAGS:
                continue
            if not element.strip():
                continue
            yield element


class EPUBTranslator:
    def __init__(
        self,
        translator: HuggingFaceTranslator,
        glossary: GlossaryPreserver,
        batch_size: int = 8,
    ) -> None:
        self.translator = translator
        self.glossary = glossary
        self.batch_size = batch_size

    def translate_item(self, item: epub.EpubItem) -> None:
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text_nodes = list(_iter_text_nodes(soup))
        LOGGER.debug("Translating %d text nodes", len(text_nodes))

        batch: List[str] = []
        node_refs: List[tuple[NavigableString, dict[str, str]]] = []

        def flush_batch() -> None:
            if not batch:
                return
            translations = self.translator.translate_batch(batch)
            for (node, placeholders), translated in zip(node_refs, translations):
                node.replace_with(self.glossary.restore(translated, placeholders))
            batch.clear()
            node_refs.clear()

        for node in text_nodes:
            protected = self.glossary.protect(str(node))
            batch.append(protected.text)
            node_refs.append((node, protected.placeholders))
            if len(batch) >= self.batch_size:
                flush_batch()
        flush_batch()

        item.set_content(str(soup).encode("utf-8"))

    def translate_book(self, input_path: Path, output_path: Path, add_metadata: bool = True) -> None:
        book = epub.read_epub(str(input_path))
        items = list(book.get_items())
        LOGGER.info("Loaded EPUB with %d items", len(items))

        for item in items:
            if item.get_type() != ebooklib.ITEM_DOCUMENT:
                continue
            LOGGER.info("Translating item %s", item.get_name())
            self.translate_item(item)

        if add_metadata:
            identifier = _get_first_metadata(book, "DC", "identifier") or input_path.stem
            book.set_identifier(f"{identifier}-translated")
            title = _get_first_metadata(book, "DC", "title") or input_path.stem
            book.set_title(f"{title} (ID Translation)")
            book.set_language("id")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(output_path), book)
        LOGGER.info("Translated EPUB saved to %s", output_path)
