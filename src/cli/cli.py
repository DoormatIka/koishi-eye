
import argparse

from typing import cast
from pathlib import Path

from wrappers import scan_from_directory, MethodAction

class CLI:
    parser: argparse.ArgumentParser
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Fuzzy duplicate image finder.")
        _ = self.parser.add_argument("-i", "--input", 
                                help="A folder to scan.")
        _ = self.parser.add_argument("-d", "--delete", 
                                action='store_true', 
                                help="Enable automatic deletion of files.")
        _ = self.parser.add_argument("-m", "--method", 
                                type=MethodAction, 
                                choices=list(MethodAction), 
                                help="Choose what method to scan the folder with.")

    async def run_cli(self):
        args = self.parser.parse_args()
        inp = str(args.input) # pyright: ignore[reportAny]
        method = cast(MethodAction, args.method)

        if len(inp) <= 0:
            self.parser.print_help()
            return
        dir_path = Path(inp)
        if not dir_path.is_dir():
            self.parser.print_help()
            return

        nearest_matches = await scan_from_directory(dir_path, choice=method)
        for img1, img2 in nearest_matches:
            print(
                f"Left: {img1.path}\n" + 
                    f"\tRight: {img2.path}\n" + 
                    f"\tGlobal Difference: {abs(img1.hash - img2.hash)}\n"
            )
        print(f"{len(nearest_matches)} matches found. Finished.")

