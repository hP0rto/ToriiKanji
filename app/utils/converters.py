"""
Image conversion utilities for ToriiKanji.
Handles conversions between PIL Images and Qt QPixmaps.
"""

import numpy as np
from PIL import Image
from PyQt6.QtGui import QImage, QPixmap


def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    """Convert a PIL Image to a Qt QPixmap for display in the UI."""
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")

    width, height = pil_image.size
    data = pil_image.tobytes("raw", "RGB")

    qimage = QImage(
        data,
        width,
        height,
        width * 3,  # 3 bytes per pixel (RGB)
        QImage.Format.Format_RGB888
    )

    return QPixmap.fromImage(qimage)


def qpixmap_to_pil(pixmap: QPixmap) -> Image.Image:
    """Convert a Qt QPixmap to a PIL Image for use with Tesseract."""
    qimage: QImage = pixmap.toImage()

    ptr = qimage.bits()
    ptr.setsize(qimage.height() * qimage.bytesPerLine())
    arr = np.array(ptr).reshape(qimage.height(), qimage.width(), 4)

    pil_img = Image.fromarray(arr, mode="RGBA")
    return pil_img
