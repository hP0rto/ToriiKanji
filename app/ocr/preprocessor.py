"""
Image pre-processing pipeline for OCR accuracy improvement.
Uses Pillow only (no OpenCV dependency).

Pipeline: grayscale → contrast enhancement → threshold (binarization)
"""

from PIL import Image, ImageEnhance, ImageFilter


def to_grayscale(image: Image.Image) -> Image.Image:
    """Convert image to grayscale (L mode)."""
    return image.convert("L")


def enhance_contrast(image: Image.Image, factor: float = 2.0) -> Image.Image:
    """
    Enhance image contrast.
    factor > 1.0 increases contrast, < 1.0 decreases it.
    """
    enhancer = ImageEnhance.Contrast(image)
    return enhancer.enhance(factor)


def enhance_sharpness(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """
    Enhance image sharpness to make text edges clearer.
    factor > 1.0 increases sharpness.
    """
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def apply_threshold(image: Image.Image, threshold: int = 128) -> Image.Image:
    """
    Apply binary threshold to image.
    Pixels above threshold become white, below become black.
    Best used on grayscale images.
    """
    if image.mode != "L":
        image = image.convert("L")
    return image.point(lambda p: 255 if p > threshold else 0, mode="1")


def remove_noise(image: Image.Image) -> Image.Image:
    """
    Apply median filter to reduce noise.
    Useful for screenshots with compression artifacts.
    """
    return image.filter(ImageFilter.MedianFilter(size=3))


def preprocess(image: Image.Image, enable: bool = True) -> Image.Image:
    """
    Full pre-processing pipeline for OCR.
    
    Steps:
        1. Convert to grayscale
        2. Remove noise (median filter)
        3. Enhance contrast
        4. Enhance sharpness
        5. Apply binary threshold
    
    Args:
        image: Input PIL Image
        enable: If False, returns the image unchanged
        
    Returns:
        Pre-processed PIL Image ready for OCR
    """
    if not enable:
        return image

    processed = to_grayscale(image)
    processed = remove_noise(processed)
    processed = enhance_contrast(processed, factor=2.0)
    processed = enhance_sharpness(processed, factor=1.5)
    processed = apply_threshold(processed, threshold=140)

    return processed
