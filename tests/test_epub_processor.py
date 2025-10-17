from __future__ import annotations

from pathlib import Path

from ebooklib import epub

from epub_translator.epub_processor import EPUBTranslator
from epub_translator.glossary import GlossaryPreserver


class DummyTranslator:
    def translate_batch(self, sentences):
        return list(sentences)


def _build_sample_epub(path: Path) -> None:
    book = epub.EpubBook()
    book.set_title("Sample Book")
    book.set_language("en")

    chapter = epub.EpubHtml(title="Chapter 1", file_name="chapter1.xhtml", lang="en")
    chapter.content = "<html><body><p>Hello world.</p></body></html>"

    book.add_item(chapter)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.toc = (chapter,)
    book.spine = ["nav", chapter]

    epub.write_epub(str(path), book)


def test_translate_book_sets_metadata_when_missing(tmp_path):
    input_path = tmp_path / "input.epub"
    output_path = tmp_path / "output.epub"
    _build_sample_epub(input_path)

    processor = EPUBTranslator(
        translator=DummyTranslator(),
        glossary=GlossaryPreserver(),
        batch_size=4,
    )

    processor.translate_book(input_path=input_path, output_path=output_path)

    translated_book = epub.read_epub(str(output_path))

    identifier_entries = translated_book.get_metadata("DC", "identifier")
    assert identifier_entries
    assert any(value.endswith("-translated") for value, _ in identifier_entries)

    title_entries = translated_book.get_metadata("DC", "title")
    assert title_entries
    assert any(value.endswith("(ID Translation)") for value, _ in title_entries)

    language_entries = translated_book.get_metadata("DC", "language")
    assert language_entries
    assert any(value == "id" for value, _ in language_entries)
