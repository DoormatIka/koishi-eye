
from PIL import Image
from src.finders.types import ImagePair
from src.hashers.types import CombinedImageHash

MATCH_THRESHOLD = 5


def is_similar_image(img1: CombinedImageHash, img2: CombinedImageHash) -> ImagePair | None:
    if img1.path != img2.path and abs(img1.hash - img2.hash) < MATCH_THRESHOLD:
        return img1, img2
    return None

def get_supported_extensions() -> list[str]:
    return [
        ".png", ".bmp", ".jpg", 
        ".jpeg", ".j2k", ".tif", 
        ".tiff", ".psd", ".emf", 
        ".webp", ".jpx", ".jpf", 
        ".ps", ".avif", ".j2c", 
        ".jp2", ".jpe"
    ]

    """
    not_allowed_ext = [".gif", ".xpm"]
    ext_reading = {ext for ext, fmt in Image.registered_extensions().items() if fmt in Image.OPEN}
    for ext in not_allowed_ext:
        ext_reading.remove(ext)
    return ext_reading
    """
