from typing import Callable

import numpy as np
import annoy as ann
import tkinter as tk
import imagehash

from PIL import Image, ImageTk
from PIL.Image import Image as PILImage
from pathlib import Path


tkwin = tk.Tk()

def alpharemover(image: Image.Image):
	if image.mode != 'RGBA':
		return image
	canvas = Image.new('RGBA', image.size, (255, 255, 255, 255))
	canvas.paste(image, mask=image)
	return canvas.convert('RGB')

def view_image(image: PILImage):
    new_win = tk.Toplevel(tkwin)
    new_win.title("img display")
    new_win.geometry("400x400")

    image_label = tk.Label(new_win)
    image_label.pack()
    display_image = image.resize((400, 400), Image.Resampling.NEAREST)
    tk_img = ImageTk.PhotoImage(display_image)
    _ = image_label.config(image=tk_img)
    setattr(image_label, "image", tk_img)

# plan: use phash and crop_hash to hash the images of the folder
# push both of those hashes into annoy's ANN, using a vector [phash, crop_hashes]
# - refresh the ANN index for each folder as well, to avoid stale image pointers.
#     - this can be done by getting the list of images from folder per directory
#     - and remove the renamed/deleted images from ANN via checksums of them.

# issues:
# combine phash (global) and crop_hash (per-section) 
# need to check what the crop_resistant_hash actually crops
#   what i mean by this is: what the images it passes to the hash function inside crop_resistant_hash
#   so i can tune it.
# please don't use chatgpt pleaase please.

def with_ztransform_preprocess() -> Callable[[Path], imagehash.ImageMultiHash]:
    def function(path: Path) -> imagehash.ImageMultiHash:
        image = alpharemover(Image.open(path))
        # phash global hashing
        # image = image.convert('L')
        # data = np.ascontiguousarray(image.get_flattened_data()).reshape(-1)
        # quantiles = np.arange(100)
        # quantiles_values = np.percentile(data, quantiles)
        # zdata = (np.interp(data, quantiles_values, quantiles) / 100 * 255).astype(np.uint8)
        # image.putdata(zdata)
        # return imagehash.phash(image=image)

        view_image(image)

        return imagehash.crop_resistant_hash(image=image, min_segment_size=100)

    return function

image_path = Path("/home/mualice/Downloads/G902oP0bQAAwFnO.jpg")
compared_to_path = Path("/home/mualice/Downloads/20260123_120718.jpg")

def main():
    hashit = with_ztransform_preprocess()
    hash_from = hashit(image_path)
    hash_compared = hashit(compared_to_path)
    
    hash_from.segment_hashes
    print(hash_from.matches(hash_compared))

    print(f"difference: {abs(hash_from - hash_compared)}")

    tkwin.mainloop()



if __name__ == "__main__":
    main()
