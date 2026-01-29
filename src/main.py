from pathlib import Path

import hasher
import logger


def scan_from_directory(directory: str): # prototype
    dir = Path(directory)
    imghasher = hasher.ImageHasher(logger=logger.MatchLogger(), size=16)
    finder = hasher.BruteForceFinder(hasher=imghasher)

    hashes = finder.create_hashes_from_directory(dir)
    _ = finder.get_similar_images(hashes)

    print("Finished.")

def main():
    scan_from_directory("/home/mualice/Downloads/")


if __name__ == "__main__":
    main()

