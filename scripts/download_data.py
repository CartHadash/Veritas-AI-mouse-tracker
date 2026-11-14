# ---------------------------------------------------------------------------
# PRE-HACKATHON CODE - DISCLOSED.
# This file was written by our team on 12-13 Nov 2026, before the hackathon
# started, during a feasibility test. It is reused here unchanged except for
# this notice. See docs/REUSED_CODE.md. Everything else in this repository was
# written during the hackathon weekend (14-15 Nov 2026).
# ---------------------------------------------------------------------------
"""
download_data.py - fetch the two public tremor datasets into data/.

The datasets are NOT stored in the GitHub repository (too big: 1.5 GB), so every
teammate runs this once. It only uses Python's standard library.

Run from the repository folder:
    python scripts/download_data.py              # both datasets (1.5 GB, 10-30 minutes)
    python scripts/download_data.py --only tremordb   # just the small one (7 MB)

It is safe to run again: files that already exist are skipped, and every PADS
file is checked against the official checksum list at the end.
"""

import argparse
import hashlib
import io
import os
import re
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor

# PhysioNet's official public mirror on Amazon S3 (much faster than physionet.org).
S3 = "https://physionet-open.s3.amazonaws.com/"
PADS_PREFIX = "parkinsons-disease-smartwatch/1.0.0/"
PADS_DIR = "data/pads"
TREMORDB_ZIP = "https://physionet.org/content/tremordb/get-zip/1.0.0/"
TREMORDB_DIR = "data/tremordb"


def fetch(url):
    """Download one URL and return its bytes (tries up to 4 times)."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise


def download_tremordb():
    marker = os.path.join(TREMORDB_DIR, "effect-of-deep-brain-stimulation-on-parkinsonian-tremor-1.0.0", "RECORDS")
    if os.path.exists(marker):
        print("TremorDB: already downloaded.")
        return
    print("TremorDB: downloading (3.5 MB)...")
    os.makedirs(TREMORDB_DIR, exist_ok=True)
    zipfile.ZipFile(io.BytesIO(fetch(TREMORDB_ZIP))).extractall(TREMORDB_DIR)
    print("TremorDB: done ->", TREMORDB_DIR)


def list_pads_files():
    """Ask the S3 mirror for the name of every file in the PADS dataset."""
    names, token = [], None
    while True:
        query = {"list-type": "2", "prefix": PADS_PREFIX}
        if token:
            query["continuation-token"] = token
        page = fetch(S3 + "?" + urllib.parse.urlencode(query)).decode()
        names += [k[len(PADS_PREFIX):] for k in re.findall(r"<Key>(.*?)</Key>", page) if not k.endswith("/")]
        more = re.search(r"<NextContinuationToken>(.*?)</NextContinuationToken>", page)
        if not more:
            return names
        token = more.group(1)


def download_pads_file(name):
    path = os.path.join(PADS_DIR, name)
    if os.path.exists(path):
        return 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = fetch(S3 + PADS_PREFIX + urllib.parse.quote(name))
    with open(path + ".part", "wb") as f:   # write to a temporary name first, so a
        f.write(data)                       # crash never leaves a half-written file
    os.replace(path + ".part", path)
    return 1


def download_pads():
    print("PADS: listing files...")
    names = list_pads_files()
    todo = [n for n in names if not os.path.exists(os.path.join(PADS_DIR, n))]
    print("PADS: %d files in total, %d still to download (1.5 GB in total)." % (len(names), len(todo)))
    done = 0
    with ThreadPoolExecutor(max_workers=24) as pool:   # 24 downloads at the same time
        for _ in pool.map(download_pads_file, todo):
            done += 1
            if done % 500 == 0:
                print("  %d / %d" % (done, len(todo)))

    print("PADS: checking every file against the official checksums...")
    bad = 0
    with open(os.path.join(PADS_DIR, "SHA256SUMS.txt")) as f:
        for line in f:
            expected, name = line.strip().split(" ", 1)
            path = os.path.join(PADS_DIR, name.strip())
            if not os.path.exists(path) or hashlib.sha256(open(path, "rb").read()).hexdigest() != expected:
                bad += 1
                print("  PROBLEM:", name.strip())
                if os.path.exists(path):
                    os.remove(path)   # so the next run downloads it again
    print("PADS: done, all files OK." if bad == 0 else "PADS: %d bad files removed - run this script again." % bad)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download the tremor datasets into data/")
    parser.add_argument("--only", choices=["pads", "tremordb"], help="download just one dataset")
    args = parser.parse_args()
    if not os.path.exists("scripts/download_data.py"):
        raise SystemExit("Please run this from the repository folder: python scripts/download_data.py")
    if args.only != "pads":
        download_tremordb()
    if args.only != "tremordb":
        download_pads()
