from ingestion.text import chunk_text, html_to_text


def test_chunk_text_splits_long_input():
    text = "word " * 1000
    chunks = chunk_text(text, chunk_size=200, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 220 for c in chunks)


def test_chunk_text_short_input_single_chunk():
    assert chunk_text("just a little text") == ["just a little text"]


def test_chunk_text_empty():
    assert chunk_text("   ") == []


def test_html_to_text_strips_tags_and_scripts():
    out = html_to_text("<div>Hello <b>world</b><script>bad()</script></div>")
    assert "Hello" in out and "world" in out
    assert "<" not in out
    assert "bad()" not in out
