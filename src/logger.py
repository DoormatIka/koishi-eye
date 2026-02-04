
import sys
from typing import Protocol

class BlankLogger(Protocol):
    def info(self, s: str) -> None: ...
    def warn(self, s: str) -> None: ...
    def match(self, s: str) -> None: ...
    def point(self) -> None: ...
    def next_line(self) -> None: ...

class MatchLogger:
    def info(self, s: str) -> None: # pyright: ignore[reportUnusedParameter]
        pass
    def warn(self, s: str) -> None: # pyright: ignore[reportUnusedParameter]
        pass
    def match(self, s: str) -> None:
        print(f"[MATCH] - {s}")
    def point(self) -> None:
        pass
    def next_line(self) -> None:
        pass

class Logger: # color code per log level: info, warn, match
    SAVE: str = "\033[s"
    RESTORE: str = "\033[u"
    CLEAR_DOWN: str = "\033[J"
    def __init__(self):
        _ = sys.stdout.write(self.SAVE)
        _ = sys.stdout.flush()

    def _draw(self, tag: str, s: str):
        _ = sys.stdout.write(self.RESTORE)
        _ = sys.stdout.write(self.CLEAR_DOWN)
        _ = sys.stdout.write(f"[{tag}] - {s}")
        _ = sys.stdout.flush()

    def next_line(self):
        _ = sys.stdout.write("\n")
        _ = sys.stdout.write(self.SAVE)
        _ = sys.stdout.flush()
    def info(self, s: str) -> None:
        self._draw("INFO", s)
    def warn(self, s: str) -> None:
        self._draw("WARN", s)
    def match(self, s: str) -> None:
        self.next_line()
        self._draw("MATCH", s)

    def point(self) -> None:
        return
