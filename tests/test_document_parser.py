"""
Tests for the document parser (core/document_parser.py).
"""
import io
import pytest

from core.document_parser import DocumentParser, DocumentChunker, ParsedDocument


class TestDocumentParser:
    """Tests for DocumentParser."""

    def test_parse_txt_from_bytes(self, sample_txt_file):
        result = DocumentParser.parse(sample_txt_file, "test.txt")
        assert isinstance(result, ParsedDocument)
        assert result.filename == "test.txt"
        assert result.file_type == "txt"
        assert result.word_count > 0
        assert "Login" in result.content

    def test_parse_txt_from_path(self, sample_txt_path):
        result = DocumentParser.parse(sample_txt_path)
        assert result.filename == "requirements.txt"
        assert result.file_type == "txt"
        assert "login" in result.content.lower()

    def test_parse_txt_encodings(self):
        """UTF-8 encoded text should parse correctly."""
        content = "Test with special chars: café, naïve, résumé"
        f = io.BytesIO(content.encode("utf-8"))
        result = DocumentParser.parse(f, "unicode.txt")
        assert "café" in result.content

    def test_parse_txt_latin1_fallback(self):
        """Latin-1 encoded text should be handled by fallback."""
        content = "Latin-1 text: \xe9\xe8\xea"  # é è ê in Latin-1
        f = io.BytesIO(content.encode("latin-1"))
        result = DocumentParser.parse(f, "latin.txt")
        assert len(result.content) > 0

    def test_parse_requires_filename_for_fileobj(self):
        f = io.BytesIO(b"test content")
        with pytest.raises(ValueError, match="filename is required"):
            DocumentParser.parse(f)

    def test_unsupported_format(self):
        f = io.BytesIO(b"data")
        with pytest.raises(ValueError, match="Unsupported"):
            DocumentParser.parse(f, "file.xyz")

    def test_is_supported(self):
        assert DocumentParser.is_supported("test.txt") is True
        assert DocumentParser.is_supported("test.pdf") is True
        assert DocumentParser.is_supported("test.docx") is True
        assert DocumentParser.is_supported("test.doc") is True
        assert DocumentParser.is_supported("test.jpg") is False
        assert DocumentParser.is_supported("test.xlsx") is False

    def test_get_supported_formats(self):
        formats = DocumentParser.get_supported_formats()
        assert ".txt" in formats
        assert ".pdf" in formats
        assert ".docx" in formats

    def test_parsed_document_word_count(self):
        f = io.BytesIO(b"one two three four five six seven")
        result = DocumentParser.parse(f, "count.txt")
        assert result.word_count == 7

    def test_empty_file(self):
        f = io.BytesIO(b"")
        result = DocumentParser.parse(f, "empty.txt")
        assert result.content == ""
        assert result.word_count == 0


class TestDocumentChunker:
    """Tests for DocumentChunker utility."""

    def test_short_text_no_chunking(self):
        text = "Short text that fits in one chunk."
        chunks = DocumentChunker.chunk_by_tokens(text, max_tokens=1000)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_long_text_chunked(self):
        text = "word " * 5000  # ~5000 words ≈ 5000 tokens
        chunks = DocumentChunker.chunk_by_tokens(text, max_tokens=500)
        assert len(chunks) > 1
        # Each chunk should be within limits
        for chunk in chunks:
            assert len(chunk) <= 500 * 4 + 100  # Allow small overshoot for boundary finding

    def test_estimate_tokens(self):
        text = "a" * 400  # 400 chars ≈ 100 tokens
        tokens = DocumentChunker.estimate_tokens(text)
        assert tokens == 100

    def test_summarize_sections(self):
        text = (
            "Introduction\n"
            "This is the intro.\n\n"
            "Business Rules\n"
            "Rule 1: Do this.\n"
            "Rule 2: Do that.\n\n"
            "Requirements\n"
            "Req 1: Feature A.\n"
        )
        sections = DocumentChunker.summarize_sections(text)
        assert len(sections) >= 2  # At least "Business Rules" and "Requirements"
