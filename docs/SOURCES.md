# Sources and credits (running list)

The rules require citing **every** dataset, pretrained model, library, tutorial and AI tool.
Add to this file the moment you start using something; the write-up's "Sources" section is
copied from here at the end.

## Datasets

- PADS - Parkinsons Disease Smartwatch dataset v1.0.0, PhysioNet,
  https://doi.org/10.13026/m0w9-zx22 (CC BY-NC-SA 4.0). Full citation in `DATASETS.md`.
- Effect of Deep Brain Stimulation on Parkinsonian Tremor (TremorDB), PhysioNet,
  https://doi.org/10.13026/C2D097 (ODC-By 1.0). Full citation in `DATASETS.md`.
- PhysioNet platform citation: see `DATASETS.md`.

## Pretrained models

- None so far. (If one is used, add name, link and licence here.)

## AI services used inside the product

- Claude API (Anthropic) for the in-app assistant. Model: to be filled in when built.

## Libraries

Installed in step 1 (exact versions in `requirements.txt`). Add new ones here when first used.

- NumPy, https://numpy.org (arrays and maths)
- pandas, https://pandas.pydata.org (tables)
- SciPy, https://scipy.org (signal filters, frequency spectra)
- scikit-learn, https://scikit-learn.org (classic machine learning: the detector v1)
- Matplotlib, https://matplotlib.org (charts)
- PyTorch, https://pytorch.org (neural networks: the corrector)
- FastAPI, https://fastapi.tiangolo.com (the local web server)
- Uvicorn, https://www.uvicorn.org (runs the FastAPI server)
- Anthropic Python SDK, https://github.com/anthropics/anthropic-sdk-python (Claude API)
- python-dotenv, https://github.com/theskumar/python-dotenv (reads the API key from `.env`)
- pytest, https://pytest.org (automatic tests)
- joblib, https://joblib.readthedocs.io (saves the trained detector; installed with scikit-learn)
- scikit-learn's HistGradientBoostingClassifier / Regressor and permutation importance,
  https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting
  (the detector v1 model and its "which features mattered" check)

## AI tools used while building

- Claude Code (Anthropic): planning, writing and testing most of the code.
- ChatGPT (OpenAI): write-up and video script drafting.
- Add any others here.

## Papers and algorithms

- One Euro filter: Casiez, Roussel, Vogel (2012), "1€ Filter: A Simple Speed-based Low-pass
  Filter for Noisy Input in Interactive Systems", CHI 2012. Used as a baseline.
- Kalman filter: Kalman (1960). Used as a baseline.
- Microsoft Research work on tremor from cursor movement: NOT YET VERIFIED (see `DATASETS.md`
  section 5). Fill in authors, year, title and link, or delete this line.

## Our own pre-hackathon work

- See `REUSED_CODE.md`.

## Tutorials and other code

- None so far.
