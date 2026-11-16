"""
check_results.py - make sure RESULTS.md contains no invented number.

Every number in evaluation/results/RESULTS.md must appear in a file a script generated
(evaluation/results/*.md and evaluation/results/failures/*.md, except RESULTS.md itself).
A few numbers are definitions, not results (the window length, the frequency band, the step
numbers...); they are listed below with the reason. Anything else that cannot be found makes
this script fail and print it.

Run from the repository folder:
    python evaluation/check_results.py
"""

import re
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
NUMBER = re.compile(r"\d+(?:\.\d+)?%?")

# Numbers that are definitions or design choices, not measured results.
DEFINITIONS = {
    "2.56": "detector window length in seconds",
    "10.24": "length of a tremor library segment in seconds",
    "5.12": "corrector sequence length in seconds",
    "0.64": "corrector input: 64 steps of 10 ms",
    "3": "3-12 Hz tremor band; also '3 px' size boundary; also counts like '3 seconds'",
    "12": "3-12 Hz tremor band",
    "10": "10 ms step; '10 px' size boundary; groups 'under 10 people'",
    "19": "the detector reads 19 measurements (features.py FEATURE_NAMES)",
    "20%": "cut-off rule: at most 20% missed on validation",
    "0.5": "smoothness penalty 0.5; 0.5x tremor size",
    "2": "2x tremor size / hand travel; penalty 2",
    "8": "penalty 8",
    "42": "random seed of the split",
    "60": "age band boundary (under 60, 60-69)",
    "69": "age band boundary (60-69); also a result in demo_modes_test.md",
    "70": "age band boundary (70 and over)",
    "0.2": "moving-average window length in seconds",
    "1": "list numbering / v1",
    "4": "v4 / list numbering",
    "5": "list numbering / '5 Hz' wording in the failure summary",
    "100": "100% in the always-no row; 100 samples per second",
    "0": "0 ms / 0%",
    "30": "'in 30 seconds' heading",
    "060": "PADS subject id in a chart file name",
    "0.3": "click freeze holds the cursor at most 0.3 s (FREEZE_MS in web/app.js)",
}


def numbers(text):
    return NUMBER.findall(text)


def main():
    sources = [p for p in list(RESULTS.glob("*.md")) + list((RESULTS / "failures").glob("*.md"))
               if p.name != "RESULTS.md"]
    known = set()
    for path in sources:
        known.update(numbers(path.read_text(encoding="utf-8")))
    text = (RESULTS / "RESULTS.md").read_text(encoding="utf-8")
    missing = sorted({n for n in numbers(text) if n not in known and n not in DEFINITIONS},
                     key=lambda n: float(n.rstrip("%")))
    if missing:
        print("NOT FOUND in any generated results file:", ", ".join(missing))
        sys.exit(1)
    print("OK: every number in RESULTS.md is in a generated results file (%d sources) "
          "or is a listed definition." % len(sources))


if __name__ == "__main__":
    main()
