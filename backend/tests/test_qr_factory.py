import pytest

from app.services.qr_factory import PNGGenerator, QRFormatFactory, SVGGenerator


class TestQRFormatFactory:
    def test_get_png_generator(self) -> None:
        gen = QRFormatFactory.get_generator("png")
        assert isinstance(gen, PNGGenerator)

    def test_get_svg_generator(self) -> None:
        gen = QRFormatFactory.get_generator("svg")
        assert isinstance(gen, SVGGenerator)

    def test_unsupported_format_raises(self) -> None:
        with pytest.raises(ValueError, match="Unsupported format"):
            QRFormatFactory.get_generator("bmp")


class TestPNGGenerator:
    def test_generate_returns_bytes(self) -> None:
        gen = PNGGenerator()
        data = gen.generate("https://example.com")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_generate_produces_valid_png(self) -> None:
        gen = PNGGenerator()
        data = gen.generate("https://example.com")
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_content_type(self) -> None:
        gen = PNGGenerator()
        assert gen.content_type == "image/png"


class TestSVGGenerator:
    def test_generate_returns_bytes(self) -> None:
        gen = SVGGenerator()
        data = gen.generate("https://example.com")
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_generate_produces_valid_svg(self) -> None:
        gen = SVGGenerator()
        data = gen.generate("https://example.com")
        assert b"<svg" in data

    def test_content_type(self) -> None:
        gen = SVGGenerator()
        assert gen.content_type == "image/svg+xml"
