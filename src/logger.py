
import sys
from typing import Protocol
import tracemalloc

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

class Logger: # color code per log level: info, warn, match
    previous_snapshot: tracemalloc.Snapshot | None = None
    SAVE: str = "\033[s"
    RESTORE: str = "\033[u"
    CLEAR_DOWN: str = "\033[J"
    def __init__(self):
        _ = sys.stdout.write(self.SAVE)
        _ = sys.stdout.flush()
        # tracemalloc.start()

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
        snapshot = tracemalloc.take_snapshot()
        if self.previous_snapshot != None:
            s = self.previous_snapshot.compare_to(snapshot, key_type="lineno")
            print("\n")
            print("====== LISTING 5 IN COMPARISON TO PREVIOUS SNAPSHOT ======")
            for frame in s[:5]:
                print("\t", frame)

        self.previous_snapshot = snapshot


