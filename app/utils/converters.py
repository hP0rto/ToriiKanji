from PyQt6.QtGui import QPixmap, QImage
from PIL import Image
import numpy as np

def pil_to_qpixmap(pil_image: Image.Image) -> QPixmap:
    """Converte PIL.Image em QPixmap para uso no Qt."""
    
    if pil_image.mode != "RGB":
        pil_image = pil_image.convert("RGB")
    
    width, height = pil_image.size
    data = pil_image.tobytes("raw", "RGB")
    
    qimage = QImage(
        data,
        width,
        height,
        width * 3,  # 3 bytes por pixel (RGB)
        QImage.Format.Format_RGB888
    )
    
    
    return QPixmap.fromImage(qimage)

def qpixmap_to_pil(pixmap: QPixmap) -> Image.Image:
    """Converte QPixmap em PIL.Image para uso no Tessertact."""
     # QPixmap -> QImage
    qimage: QImage = pixmap.toImage()

    # Converte QImage para numpy array (RGBA8888)
    ptr = qimage.bits()
    ptr.setsize(qimage.height() * qimage.bytesPerLine())
    arr = np.array(ptr).reshape(qimage.height(), qimage.width(), 4)

    # Converte para PIL (Tesseract aceita)
    pil_img = Image.fromarray(arr, mode="RGBA")
    
    return pil_img