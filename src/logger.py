
from typing import override


class BlankLogger():
    def info(self, s: str) -> None: # pyright: ignore[reportUnusedParameter]
        pass
    def warn(self, s: str) -> None: # pyright: ignore[reportUnusedParameter]
        pass
    def match(self, s: str) -> None: # pyright: ignore[reportUnusedParameter]
        pass

class MatchLogger(BlankLogger):
    @override
    def match(self, s: str) -> None:
        print(f"[MATCH] - {s}")

class Logger(BlankLogger): # color code per log level: info, warn, match
    @override
    def info(self, s: str) -> None:
        print(f"[INFO] - {s}")
    @override
    def warn(self, s: str) -> None:
        print(f"[WARN] - {s}")
    @override
    def match(self, s: str) -> None:
        print(f"[MATCH] - {s}")

