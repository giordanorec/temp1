"""Tests for data quality filters and deduplication."""

from src.data.prepare import is_quality_text, clean_text, ExactDeduplicator


def test_quality_filter_accepts_good_text():
    text = (
        "O FarolLM e um modelo de linguagem treinado do zero. "
        "Ele utiliza uma arquitetura Transformer decoder-only com "
        "melhorias modernas como RoPE, SwiGLU e Grouped-Query Attention. "
        "O objetivo e entender profundamente todo o pipeline de criacao "
        "de modelos de linguagem, documentando cada decisao para "
        "reprodutibilidade completa."
    )
    assert is_quality_text(text)


def test_quality_filter_rejects_short():
    assert not is_quality_text("Too short.")


def test_quality_filter_rejects_repetitive():
    text = "spam " * 500
    assert not is_quality_text(text)


def test_quality_filter_rejects_mostly_numbers():
    text = "12345 " * 100
    assert not is_quality_text(text)


def test_quality_filter_rejects_all_caps():
    text = "THIS IS ALL CAPS TEXT THAT GOES ON AND ON " * 20
    assert not is_quality_text(text)


def test_clean_text_normalizes():
    dirty = "  Hello\r\n\r\n\r\nworld  \t  foo  "
    cleaned = clean_text(dirty)
    assert "\r" not in cleaned
    assert "\t" not in cleaned
    assert "  " not in cleaned
    assert cleaned == "Hello\n\nworld foo"


def test_deduplicator():
    dedup = ExactDeduplicator()
    text1 = "This is a unique document about language models and training."
    text2 = "This is another document about something completely different."
    text3 = "This is a unique document about language models and training."

    assert not dedup.is_duplicate(text1)
    assert not dedup.is_duplicate(text2)
    assert dedup.is_duplicate(text3)  # duplicate of text1
