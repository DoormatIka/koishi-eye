## goals

- program should be able to handle a large amount of images.

## main

using PyNNDescent as the ANN.

- get image paths from folder recursively
  - `path.Path().glob("*.[png][webp] etc etc...")` to list all the files recursively
- use phash and crop_hash to hash the images of the folder
- push both of those hashes into the ANN, using a vector [phash, crop_hashes]
- we can loop through the pictures and query the ANN to see what images are a _really_ close match, those will be classified as duplicates.

- keep the ANN in disk until the program closes, then it should delete the ANN.

building the index is an `O(n * log(n) * d)` operation, and querying is an `O(log(n) * d)` operation.

- `n` is the number of files
- `d` are the dimensions of the ANN. For a (16x16) fingerprint, it will be 256.

bonus features:

- have a bar that says how many files are finished indexing and compared to.
  - use OS-specific commands for this: linux - `find . -type f | wc -l`, win - `(Get-ChildItem -Recurse -File | Measure-Object).Count`
- auto-delete worse looking images by looking into image quality metrics

## commands

`flet build linux` - compiling into a binary, [help](https://docs.flet.dev/cli/flet-build/#usage)

`flet run -r src/main.py` - run developer mode

## memory hunting

`/usr/bin/time -v uv run src/main.py` - basic memory + time benchmarking

`scalene run --outfile report.json src/main.py -i /home/mualice/Downloads/`

`scalene view --standalone report.json`
