"""Optional local log of pointer samples, and the "delete my data" function.

DECISION L1 = A: the session normally lives only in memory. If the user turns saving on,
samples go to a CSV file in local_logs/ (ignored by git; it never leaves the laptop).
Each file holds only time, x and y. delete_all_logs() empties the folder.

Option B (a history across days, to show trends) is a possible future extension.
"""

from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "local_logs"


class SampleLog:
    """Appends samples to local_logs/pointer_<date>_<time>.csv as lines of t,x,y."""

    def __init__(self):
        LOG_DIR.mkdir(exist_ok=True)
        name = "pointer_%s.csv" % datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = LOG_DIR / name
        self.file = open(self.path, "a", encoding="utf-8")
        self.file.write("t,x,y\n")
        self.lines_since_flush = 0

    def write(self, sample):
        self.file.write("%.4f,%.1f,%.1f\n" % (sample["t"], sample["x"], sample["y"]))
        self.lines_since_flush += 1
        if self.lines_since_flush >= 100:     # write to disk about once a second
            self.file.flush()
            self.lines_since_flush = 0

    def close(self):
        self.file.close()


def delete_all_logs():
    """Delete every file in local_logs/. Returns how many files were deleted."""
    if not LOG_DIR.exists():
        return 0
    deleted = 0
    for path in LOG_DIR.iterdir():
        if path.is_file():
            path.unlink()
            deleted += 1
    return deleted
