import io
from abc import ABC, abstractmethod

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.svg import SvgPathImage

from app.config import settings


class QRGenerator(ABC):
    @abstractmethod
    def generate(self, url: str) -> bytes: ...

    @property
    @abstractmethod
    def content_type(self) -> str: ...


class PNGGenerator(QRGenerator):
    content_type = "image/png"

    def generate(self, url: str) -> bytes:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=settings.qr_default_size,
            border=settings.qr_default_border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(image_factory=StyledPilImage)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()


class SVGGenerator(QRGenerator):
    content_type = "image/svg+xml"

    def generate(self, url: str) -> bytes:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=settings.qr_default_size,
            border=settings.qr_default_border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(image_factory=SvgPathImage)
        buffer = io.BytesIO()
        img.save(buffer)
        return buffer.getvalue()


class QRFormatFactory:
    _generators: dict[str, type[QRGenerator]] = {
        "png": PNGGenerator,
        "svg": SVGGenerator,
    }

    @classmethod
    def get_generator(cls, format: str) -> QRGenerator:
        gen_class = cls._generators.get(format)
        if not gen_class:
            raise ValueError(f"Unsupported format: {format}")
        return gen_class()
