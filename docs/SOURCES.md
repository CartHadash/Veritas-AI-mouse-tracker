# Sources and credits (running list)

The rules require citing **every** dataset, pretrained model, library, tutorial and AI tool.
Add to this file the moment you start using something; the write-up's "Sources" section is
copied from here at the end.

## Datasets

- PADS - Parkinsons Disease Smartwatch dataset v1.0.0, PhysioNet,
  https://doi.org/10.13026/m0w9-zx22 (CC BY-NC-SA 4.0). Full citation in `DATASETS.md`.
- Effect of Deep Brain Stimulation on Parkinsonian Tremor (TremorDB), PhysioNet,
  https://doi.org/10.13026/C2D097 (ODC-By 1.0). Full citation in `DATASETS.md`.
- PhysioNet platform citation: see `DATASETS.md`. The download script uses PhysioNet's public
  mirror on Amazon S3 (https://physionet-open.s3.amazonaws.com/).

## Pretrained models

- None so far. (If one is used, add name, link and licence here.)

## AI services used inside the product

- Claude API (Anthropic) for the in-app assistant, https://docs.claude.com. Model:
  Claude Sonnet 5.5 (`claude-sonnet-5-5`), effort `low`, streamed, with the server-side
  refusal fallback (beta `server-side-fallback-2026-07-01`). It receives only the session
  summary numbers. Called with the Anthropic Python SDK (listed under Libraries).

## Libraries

Installed in step 1 (exact versions in `requirements.txt`). Add new ones here when first used.

- NumPy, https://numpy.org (arrays and maths)
- pandas, https://pandas.pydata.org (installed in step 1; not used by our code so far)
- SciPy, https://scipy.org (signal filters, frequency spectra)
- scikit-learn, https://scikit-learn.org (classic machine learning: detectors v1 and v2)
- Matplotlib, https://matplotlib.org (charts)
- PyTorch, https://pytorch.org (neural networks: the corrector; trained with the Adam optimiser)
- FastAPI, https://fastapi.tiangolo.com (the local web server)
- Uvicorn, https://www.uvicorn.org (runs the FastAPI server)
- Anthropic Python SDK, https://github.com/anthropics/anthropic-sdk-python (Claude API)
- python-dotenv, https://github.com/theskumar/python-dotenv (reads the API key from `.env`)
- certifi, https://github.com/certifi/python-certifi (trusted certificates for secure downloads
  in `scripts/download_data.py`; python.org Python on macOS has none of its own)
- pytest, https://pytest.org (automatic tests)
- websockets, https://websockets.readthedocs.io (used by `server/test_ws.py`; installed with
  uvicorn[standard])
- joblib, https://joblib.readthedocs.io (saves the trained detector; installed with scikit-learn)
- scikit-learn's HistGradientBoostingClassifier / Regressor and permutation importance,
  https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting
  (the detector v1 model and its "which features mattered" check)
- threadpoolctl, https://github.com/joblib/threadpoolctl (keeps live detector calls on one
  thread; installed with scikit-learn)
- PyObjC (pyobjc-framework-Quartz), https://pyobjc.readthedocs.io (macOS only: reads the
  pointer position for the whole-laptop tracker via Apple's Quartz `CGEventGetLocation`,
  https://developer.apple.com/documentation/coregraphics/cgevent/location)

- ui-sdk web components, `@ui-sdk/web` version 0.1.0-beta.1 (Vercel Labs, Apache-2.0 licence),
  https://ui-sdk.dev . The tabs, filter choice, switches, slider, meter and the assistant's
  pop-up window in `web/index.html`. Not installed with pip or npm: the package's `browser`
  folder is copied into `web/vendor/ui-sdk/` (its licence file is there too). Added Sat 14 Nov 21:57 CET.

- Fonts for the interface (added Sun 15 Nov 12:54 CET), both under the SIL Open Font License 1.1, taken
  from the Fontsource packages `@fontsource-variable/bricolage-grotesque` and
  `@fontsource-variable/instrument-sans` (version 5.3.0) and stored in `web/fonts/` with
  their licence files: **Bricolage Grotesque** (Atelier Triay,
  https://github.com/ateliertriay/bricolage) for headings and numbers; **Instrument Sans**
  (Instrument, https://github.com/Instrument/instrument-sans) for text.

## AI tools used while building

- The ui-sdk agent skill (`npx skills add vercel-labs/ui --skill ui-sdk`, saved in
  `.agents/skills/ui-sdk/`): the library's own instructions for AI assistants. Used by the
  leader's agent for the redesign. Added Sat 14 Nov 21:57 CET.

- Claude Code (Anthropic): planning, writing and testing most of the code.
- ChatGPT (OpenAI): write-up and video script drafting.
- Add any others here.

## Papers and algorithms

- One Euro filter: Casiez, Roussel, Vogel (2012), "1€ Filter: A Simple Speed-based Low-pass
  Filter for Noisy Input in Interactive Systems", CHI 2012. Used as a baseline. Our version
  (`baselines/classical_filters.py`, rewritten Sat 14 Nov) follows the authors' reference code,
  https://github.com/casiez/OneEuroFilter (read, not copied: speed from the previous smoothed value).
- Kalman filter: Kalman, R. E. (1960), "A New Approach to Linear Filtering and Prediction
  Problems", Journal of Basic Engineering 82(1). Used as a baseline.
- Gradient boosting: Friedman, J. H. (2001), "Greedy function approximation: a gradient
  boosting machine", Annals of Statistics 29(5). The detector model (scikit-learn's version).
- Permutation importance ("which features mattered"): Breiman, L. (2001), "Random Forests",
  Machine Learning 45. The idea of shuffling one feature to see how much worse a model gets.
- Adam optimiser: Kingma, D. P. & Ba, J. (2014), "Adam: A Method for Stochastic Optimization",
  arXiv:1412.6980. Used to train the corrector.
- Fitts's law (pointing time grows with distance / target size): Fitts, P. M. (1954), "The
  information capacity of the human motor system in controlling the amplitude of movement",
  Journal of Experimental Psychology 47(6). Used for the realistic synthetic reaches (step 4);
  the constants are our choice.
- Bootstrap (redrawing people with repeats to get uncertainty ranges): Efron, B. (1979),
  "Bootstrap Methods: Another Look at the Jackknife", Annals of Statistics 7(1). Used in
  `evaluation/failure_extras.py` (step 9).
- Apple Quartz Event Services (event taps, `CGEventTapCreate`, `CGEventSetLocation`,
  `CGWarpMouseCursorPosition`), used through pyobjc for B3 (`systemwide/run.py`):
  https://developer.apple.com/documentation/coregraphics/quartz_event_services
- Pointer Lock (browser feature used by "Lower sensitivity"): W3C Pointer Lock specification,
  https://www.w3.org/TR/pointerlock-2/
- Minimum-jerk model of human reaching: Flash, T. & Hogan, N. (1985), "The coordination of arm
  movements: an experimentally confirmed mathematical model", Journal of Neuroscience 5(7).
  Used for the synthetic reaches (step 4).
- Dilated causal convolutions: van den Oord, A. et al. (2016), "WaveNet: A Generative Model for
  Raw Audio", arXiv:1609.03499. The idea behind the corrector's layer layout (step 8).
- White, R. W. & Horvitz, E. (2019), "Population-scale hand tremor analysis via anonymized
  mouse cursor signals", npj Digital Medicine, https://doi.org/10.1038/s41746-019-0171-4
  (free: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6760188/). Related work (Microsoft
  Research): tremor estimated from millions of users' anonymised cursor logs; suggests opt-in
  monitoring. Ours is the personal, on-device version. Verified by the team leader's agent,
  Sat 14 Nov.
- PADS original publication: Varghese, J. et al. (2024), "Machine Learning in the Parkinson's
  disease smartwatch (PADS) dataset", npj Parkinson's Disease 10:9,
  https://doi.org/10.1038/s41531-023-00625-7. Cite together with the PADS dataset above.

- British Dyslexia Association, "Dyslexia friendly style guide" (sans-serif fonts such as
  Verdana, larger spacing between letters, words and lines): the basis of the page's
  "Easier-to-read text" switch (`web/reading.js`).
- OpenDyslexic font by Abbie Gonzalez (https://opendyslexic.org), SIL Open Font License 1.1:
  the font of the "Easier-to-read text" switch. Regular and bold `.woff2` files from the
  `@fontsource/opendyslexic` package, version 5.3.0 (via cdn.jsdelivr.net), stored in
  `web/fonts/` with the licence text (`OPENDYSLEXIC_LICENSE.txt`).
- Flash, T. and Hogan, N. (1985), "The coordination of arm movements: an experimentally
  confirmed mathematical model" (the smooth "minimum jerk" reach): the shape of the simulated
  reach in `evaluation/systemwide_clicks.py`.

## Our own pre-hackathon work

- Dataset research only (`DATASETS.md`); no pre-hackathon code is left (see `REUSED_CODE.md`).

## Tutorials and other code

- Web Speech API (`speechSynthesis`), built into the browser: the "Read aloud" button under the
  assistant's answers. No library, no key; on macOS it uses the system's own voices
  (https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis).
