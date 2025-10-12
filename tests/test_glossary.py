from epub_translator.glossary import GlossaryPreserver


def test_protect_and_restore_preserves_terms():
    glossary = GlossaryPreserver(["Fenrir", "Mjolnir"])
    protected = glossary.protect("Fenrir mengangkat Mjolnir dengan gagah.")
    assert "Fenrir" not in protected.text
    assert "Mjolnir" not in protected.text

    restored = glossary.restore("Fenrir mengangkat Mjolnir dengan gagah.", protected.placeholders)
    assert restored == "Fenrir mengangkat Mjolnir dengan gagah."


def test_with_defaults_includes_animals():
    glossary = GlossaryPreserver.with_defaults()
    protected = glossary.protect("Seekor dragon terbang di langit.")
    assert "dragon" not in protected.text
