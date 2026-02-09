
from PIL import Image
from src.finders.types import ImagePair
from src.hashers.types import CombinedImageHash

MATCH_THRESHOLD = 5


def is_similar_image(img1: CombinedImageHash, img2: CombinedImageHash) -> ImagePair | None:
    if img1.path != img2.path and abs(img1.hash - img2.hash) < MATCH_THRESHOLD:
        return img1, img2
    return None

def get_supported_extensions():
    ext_reading = {ext for ext, fmt in Image.registered_extensions().items() if fmt in Image.OPEN}
    ext_reading.remove(".gif")
    return ext_reading       
