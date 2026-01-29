from pathlib import Path

import hasher
import logger

# issues:
# combine phash (global) and crop_hash (per-section) 
# need to check what the crop_resistant_hash actually crops
#   what i mean by this is: what the images it passes to the hash function inside crop_resistant_hash
#   so i can tune it.
# please don't use chatgpt pleaase please.


def scan_from_directory(directory: str): # prototype
    dir = Path(directory)
    imghasher = hasher.ImageHasher(logger=logger.Logger(), size=16)
    finder = hasher.BruteForceFinder(hasher=imghasher)

    hashes = finder.create_hashes_from_directory(dir)
    _ = finder.get_similar_images(hashes)

    print("Finished.")

def main():
    scan_from_directory("/home/mualice/Downloads/")


if __name__ == "__main__":
    main()

