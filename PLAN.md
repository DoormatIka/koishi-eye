## limitations

- program should be able to handle any number of images
  - never store the entire folder's images in memory long-term, e.g: pushing images from outside the main loop

## stage 1: main

- get images from folder recursively
  - `path.Path().glob("*.[png][webp] etc etc...")` to list all the files recursively
- use phash and crop_hash to hash the images of the folder
- push both of those hashes into annoy's ANN, using a vector [phash, crop_hashes]
- we can loop through annoy's ANN to see what images are a _really_ close match, those will be classified as duplicates.

- keep the ANN in disk until the program closes, then it should delete the ANN.

building the index is an `O(n * log(n) * d)` operation, and querying is an `O(log(n) * d)` operation.

- `n` is the number of files
- `d` are the dimensions of the ANN. For a (16x16) fingerprint, it will be 256.

## stage 2: optimizations

1. store the ANN + a file index to re-use old calculated data.
   - get hash (xxHash) per file, pass it into an SQLite database (folder) -> [files]
   - take a snapshot of the folder and refresh the ANN based on that.
   - store ANN in `data/` folder, assuming we can use PyInstaller to have our own folder.

   this can precalculate indexing the entire folder or any subfolders

```sql
-- this entire database is to refresh the ANN index for reuse.
-- we will use a merkle tree for this, similar to what git uses.

-- problem: seeing if the new folder is the same as what is stored in the sqlite database
-- solutions: using last_modified_time, total_size, and as a last resort, using buzhash
CREATE TABLE folder_snapshot (
    path TEXT,
    name TEXT,
    -- the combined buzhash from the file_snapshots
    buzhash BLOB,
    -- we can go directly to file_snapshot cache to files that are newer than the sqlite folder
    last_modified_time INTEGER,
    total_size INTEGER,

    PRIMARY KEY (path)
)

-- we take a snapshot for each file processed by the program for reusing
-- this is to keep track of stale images that do not exist or have been changed after the program's last run
CREATE TABLE file_snapshot (
    path TEXT,
    parent_path TEXT,
    snapshot_id INTEGER, -- 1 for 'old', 2 for 'new'
    last_modified_time INTEGER,
    size INTEGER,
    ann_index BLOB, -- the supposed connection to the ANN's index

    crop_hash TEXT,
    phash TEXT, -- if ann_index is impossible to implement,
        -- we'll stick with using the hash to approximate if the file is the same in ANN.

    buzhash TEXT, -- a proper hash of the file, can be used to grab elements from the ANN as well.

    folder TEXT,

    PRIMARY KEY (path, parent_path)
    FOREIGN KEY (folder) REFERENCES folder_snapshot(path)
);
CREATE INDEX idx_parent_path ON file_snapshot(parent_path);
CREATE INDEX idx_hash ON file_snapshot(phash);
```

If I somehow implement all of this, I can do basic deduplication as well as the main function of this program.
