# Datasets: facts, licences, citations

Researched before the hackathon (allowed: "browse datasets beforehand"). Everything here
was checked by downloading and opening the data, unless marked otherwise.

Get the data with `python scripts/download_data.py` (1.5 GB, 10–30 minutes). It lands in
`data/`, which is never committed.

## The most important fact

**Neither dataset contains mouse data.** One measures wrist movement, the other fingertip
velocity. Turning those into cursor pixels is **our own assumption** and must be described
that way everywhere. We could not find any public dataset of high-rate mouse movement from
people with tremor.

## 1. PADS: Parkinson's Disease Smartwatch dataset

| | |
|---|---|
| Location after download | `data/pads/` |
| What was measured | Two Apple Watches (one per wrist) during 11 short movement tasks |
| Subjects | **469**: 276 Parkinson's, 79 healthy, 60 other movement disorders, 28 essential tremor, 15 atypical Parkinsonism, 11 multiple sclerosis |
| Recording files | 10,318 (469 subjects × 11 tasks × 2 wrists) |
| File format | Plain text, comma-separated, no header: `movement/timeseries/060_Relaxed_RightWrist.txt` |
| Columns (7) | time (s), accelerometer X/Y/Z (g), gyroscope X/Y/Z (rad/s) |
| Sampling rate | **100 Hz** |
| Length | 10.24 s (1024 rows); 20.48 s for `Relaxed`, `RelaxedTask`, `Entrainment` |
| Per-person info | `patients/patient_XXX.json`: `condition` (diagnosis), `age`, `gender`, `handedness`, `height`, `weight`, free-text `disease_comment` |
| Same info as a table | `preprocessed/file_list.csv` |

Tasks by tremor type:

- **Rest:** `Relaxed`, `RelaxedTask` (resting while doing mental arithmetic).
- **Postural (holding a position):** `StretchHold`, `LiftHold`, `HoldWeight`, `Entrainment`.
- **Action (moving on purpose, closest to using a mouse):** `PointFinger`, `DrinkGlas`,
  `TouchNose`, `TouchIndex`, `CrossArms`.

Labels:

- **Diagnosis per person: yes** (`condition`).
- **Tremor per recording: no.** Nothing says "this recording contains tremor".
- **Severity: no.** No clinical score. 40 Parkinson's patients are described as
  "tremordominant" in `disease_comment`.
- **Age and sex: yes**, which lets us check the model across groups, as the Health brief asks.

Known good example: subject 060 (Parkinson's), right wrist, `Relaxed`: a tremor peak at
4.30 Hz with 99% of gyroscope power between 3 and 12 Hz.

Quirks: the official page describes 6 columns but files have 7 (time first). `LICENSE.txt`
in the download is an empty file; the licence is stated on the web page.

**Licence:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0):
credit the authors, no commercial use, share anything built from it under the same licence.

**Cite as:**

> Varghese, J., Brenner, A., Plagwitz, L., van Alen, C., Fujarski, M., & Warnecke, T.
> (2024). PADS - Parkinsons Disease Smartwatch dataset (version 1.0.0). PhysioNet.
> RRID:SCR_007345. https://doi.org/10.13026/m0w9-zx22

The PhysioNet page also lists an original publication to cite. **To do before submitting:**
copy its exact wording from
https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/

## 2. TremorDB: Effect of Deep Brain Stimulation on Parkinsonian Tremor

| | |
|---|---|
| Location after download | `data/tremordb/effect-of-deep-brain-stimulation-on-parkinsonian-tremor-1.0.0/` |
| What was measured | A laser measuring the **velocity of the index fingertip** at rest |
| Subjects | **16**, all Parkinson's: 8 high-amplitude tremor (g1–s8), 8 low-amplitude (g9–s16) |
| Recordings | 101 files in 16 folders, about 60 s each |
| File format | Plain text, **one number per line**; load with `numpy.loadtxt` |
| Sampling rate | **100 Hz** |

Everything is encoded in the file name, e.g. `s6rof.let`: subject 6 (electrode in STN),
`r` rest tremor, `o` stimulation off (`e` = on), `f` medication off (`n` = on), `.let` /
`.rit` left / right finger. Folder names end in `h` (high-amplitude subjects) or `l` (low).

- **Strongest tremor:** `rofh/` (stimulation off, medication off, high-amplitude subjects),
  then `r15ofh/` … `r60ofh/`.
- **Little tremor:** the `…l` folders and the `ren*` folders.
- **No numeric severity score**, no age/sex per recording inside the signal files (age and
  sex per subject are in `subject_description.txt`).

Known good example: `rofh/s6rof.let`, 91 s, peak at 4.88 Hz, 98% of power in 3–12 Hz, with
a second smaller peak near 10 Hz (a harmonic).

Quirks: one axis only (a cursor needs two). Units are unreliable (header says m/s but values
reach ±1), so treat amplitude as arbitrary. The `.hea` header files are not valid for the
`wfdb` library. One header names `v5rof.rit` while the file is `v5rof.let`.

**Licence:** Open Data Commons Attribution License v1.0 (ODC-By 1.0): free to use with credit.

**Cite as:**

> Beuter, A., Titcombe, M.S., Richer, F., Gross, C., Guehl, D. (2001). Effect of deep brain
> stimulation on amplitude and frequency characteristics of rest tremor in Parkinson's
> disease. Thalamus & Related Systems, 1(3), 203–211.
> Dataset: https://doi.org/10.13026/C2D097

## 3. PhysioNet (cite alongside both)

As shown on both dataset pages on 13 Nov 2026:

> Pollard, T., Moody, B. E., Lehman, L., Gow, B., Fernandes, C., Xie, C., Johnson, A.,
> Mark, R. G., & Heldt, T. (2026). PhysioNet as a global platform for biomedical research.
> Nature Health. https://doi.org/10.1038/s44360-026-00096-z

## 4. Datasets we looked at and rejected

- **RobustPDx** (mouse and keyboard tasks, 261 people, Figshare, CC0,
  https://doi.org/10.6084/m9.figshare.32099416). Its paper says cursor position was saved
  about every 500 ms, roughly 2 samples per second. A signal sampled twice a second cannot
  contain anything faster than 1 Hz, so a 4–6 Hz tremor is invisible in it. **Do not use it
  for tremor.** (Checked from the paper and the file listing; the CSVs were not opened.)
- **Tappy keystroke data** (suggested by a teammate's AI as a fallback). Typing timing, not
  pointer movement. It would make this a different project. Only consider it if the mouse
  approach has completely failed by Saturday night. Not checked by us.

## 5. Related work to cite (verify before citing)

A teammate's AI reported that Microsoft Research (Ryen White and Eric Horvitz, around 2019)
estimated hand tremor from anonymised mouse cursor movement at population scale and
suggested opt-in monitoring as a future application. **We have not verified this paper.**
Before it goes in the write-up, find it, confirm the authors, year, title and what it
actually claims, and add the link to `docs/SOURCES.md`. If it checks out, it is useful: it
shows the idea is credible, and our project is the personal, on-device version.

## 6. Facts about the demo machine

- MacBook Pro (Apple Silicon), macOS 26. PyTorch can use the Apple GPU (`mps`).
- Pointer movement arrives at about 122 samples per second, regular timing (measured with
  the trackpad; the wireless mouse was not measured).
- macOS pointer acceleration is on. It makes fast movements travel further than slow ones,
  so on-screen tremor size is not a simple copy of hand movement. Frequency is unaffected.
