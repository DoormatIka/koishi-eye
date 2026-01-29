
class Logger: # color code per log level: info, warn, match
    def info(self, s: str) -> None:
        print(f"[INFO] - {s}")
    def warn(self, s: str) -> None:
        print(f"[WARN] - {s}")
    def match(self, s: str) -> None:
        print(f"[MATCH] - {s}")
