"""
download_data.py - fetch the two public tremor datasets from PhysioNet into data/.

Written from scratch during the hackathon (Sat 14 Nov 2026), replacing the pre-hackathon
script (team leader's decision; see docs/REUSED_CODE.md).

How it works, for each dataset:
  1. download PhysioNet's list of files with their SHA-256 checksums (a fingerprint of each
     file's exact contents: if one byte differs, the fingerprint differs);
  2. for every file in the list: if it is already on disk with the right fingerprint, skip it;
     otherwise download it, check the fingerprint, and only then put it in place.
Files come from PhysioNet's public mirror on Amazon (physionet-open.s3.amazonaws.com), which
was much faster for us than PhysioNet's own zip download. Only Python's standard library is
used. Running it again is safe: it only fetches what is missing or damaged.

Run from anywhere (it finds the repository folder itself):
    python scripts/download_data.py                  # both datasets (about 1.5 GB)
    python scripts/download_data.py --only tremordb  # just the small one (about 4 MB)
    python scripts/download_data.py --check          # only check the files on disk, download nothing

Data licences and citations: docs/DATASETS.md. The data folder is never committed to git.
"""

import argparse
import hashlib
import ssl
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR = "https://physionet-open.s3.amazonaws.com"

# name -> (PhysioNet project name and version, folder it goes into)
DATASETS = {
    "pads": ("parkinsons-disease-smartwatch/1.0.0", ROOT / "data" / "pads"),
    "tremordb": ("tremordb/1.0.0",
                 ROOT / "data" / "tremordb" / "effect-of-deep-brain-stimulation-on-parkinsonian-tremor-1.0.0"),
}
CHECKSUM_LIST = "SHA256SUMS.txt"
# Secure connections need a list of trusted certificates. Python from python.org on macOS
# does not use the Mac's own list, so we use the certifi package's list when it is installed
# (it is in requirements.txt) and the system's list otherwise (fine on Windows).
try:
    import certifi
    SECURE = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SECURE = ssl.create_default_context()
DOWNLOAD_THREADS = 8      # several files at once: most files are small, so waiting dominates
TRIES = 3


def fetch(url):
    """The bytes at url, trying a few times if the connection fails."""
    for attempt in range(1, TRIES + 1):
        try:
            with urllib.request.urlopen(url, timeout=60, context=SECURE) as response:
                return response.read()
        except OSError as error:
            if attempt == TRIES:
                raise RuntimeError("could not download %s: %s" % (url, error))
            time.sleep(2 * attempt)


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_checksum_list(text):
    """Lines of '<sha256> <relative path>' -> list of (sha256, relative path)."""
    entries = []
    for line in text.splitlines():
        if line.strip():
            checksum, name = line.split(maxsplit=1)
            entries.append((checksum.lower(), name.strip()))
    return entries


def file_url(project, name):
    return "%s/%s/%s" % (MIRROR, project, urllib.parse.quote(name))


def get_one(project, folder, checksum, name, check_only):
    """Make sure one file is on disk with the right checksum. Returns 'ok', 'fetched' or 'bad'."""
    target = folder / name
    if target.exists() and sha256_of(target) == checksum:
        return "ok"
    if check_only:
        return "bad"
    data = fetch(file_url(project, name))
    if hashlib.sha256(data).hexdigest() != checksum:
        raise RuntimeError("checksum mismatch for %s (the download was damaged; run again)" % name)
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    partial.write_bytes(data)
    partial.replace(target)              # all-or-nothing: never a half-written data file
    return "fetched"


def get_dataset(name, check_only):
    project, folder = DATASETS[name]
    print("%s: %s -> %s" % (name, project, folder.relative_to(ROOT)))
    entries = read_checksum_list(fetch(file_url(project, CHECKSUM_LIST)).decode("utf-8"))
    if not check_only:
        folder.mkdir(parents=True, exist_ok=True)
        (folder / CHECKSUM_LIST).write_text("\n".join("%s %s" % e for e in entries) + "\n", encoding="utf-8")

    counts = {"ok": 0, "fetched": 0, "bad": 0}
    bad_names = []
    with ThreadPoolExecutor(max_workers=DOWNLOAD_THREADS) as pool:
        jobs = [(n, pool.submit(get_one, project, folder, c, n, check_only)) for c, n in entries]
        for done, (file_name, job) in enumerate(jobs, start=1):
            outcome = job.result()
            counts[outcome] += 1
            if outcome == "bad":
                bad_names.append(file_name)
            if done % 1000 == 0 or done == len(jobs):
                print("  %d / %d files" % (done, len(jobs)))
    print("  already correct: %d, downloaded: %d, missing or damaged: %d" % (
        counts["ok"], counts["fetched"], counts["bad"]))
    for file_name in bad_names[:10]:
        print("    missing or damaged:", file_name)
    return counts["bad"] == 0


def main():
    parser = argparse.ArgumentParser(description="Download the PADS and TremorDB datasets from PhysioNet.")
    parser.add_argument("--only", choices=sorted(DATASETS), help="fetch just one dataset")
    parser.add_argument("--check", action="store_true", help="check the files on disk; download nothing")
    args = parser.parse_args()
    names = [args.only] if args.only else list(DATASETS)
    all_good = all([get_dataset(name, args.check) for name in names])
    if args.check:
        print("All files present and correct." if all_good else "Some files are missing or damaged: "
              "run without --check to fetch them.")
    sys.exit(0 if all_good else 1)


if __name__ == "__main__":
    main()
