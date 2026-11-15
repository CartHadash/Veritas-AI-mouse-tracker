# TAG Pointer: sources, datasets and credits

Every dataset, model, library, method and AI tool used in this project.

**This project is a prototype and is not medical advice.**

## Datasets

Neither dataset contains mouse data: one measures wrist movement, the other fingertip velocity.
Turning that movement into cursor pixels is our own assumption. We found no public dataset of
high-rate mouse movement from people with tremor. The data is downloaded with
`python scripts/download_data.py` (1.5 GB, from PhysioNet's public mirror on Amazon S3,
https://physionet-open.s3.amazonaws.com/) and is never stored in this repository.

### PADS: Parkinson's Disease Smartwatch dataset

- 469 people (276 Parkinson's, 79 healthy, 60 other movement disorders, 28 essential tremor,
  15 atypical Parkinsonism, 11 multiple sclerosis); two Apple Watches, 11 movement tasks,
  100 samples per second.
- Licence: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0).
- Varghese, J., Brenner, A., Plagwitz, L., van Alen, C., Fujarski, M., & Warnecke, T. (2024).
  PADS - Parkinsons Disease Smartwatch dataset (version 1.0.0). PhysioNet. RRID:SCR_007345.
  https://doi.org/10.13026/m0w9-zx22
- Varghese, J. et al. (2024). Machine Learning in the Parkinson's disease smartwatch (PADS)
  dataset. npj Parkinson's Disease, 10, 9. https://doi.org/10.1038/s41531-023-00625-7

### TremorDB: Effect of Deep Brain Stimulation on Parkinsonian Tremor

- 15 usable people with Parkinson's (16 described; one has no recordings); index fingertip
  velocity at rest, 100 samples per second.
- Licence: Open Data Commons Attribution License v1.0 (ODC-By 1.0).
- Beuter, A., Titcombe, M.S., Richer, F., Gross, C., Guehl, D. (2001). Effect of deep brain
  stimulation on amplitude and frequency characteristics of rest tremor in Parkinson's disease.
  Thalamus & Related Systems, 1(3), 203–211. Dataset: https://doi.org/10.13026/C2D097

### PhysioNet (cited alongside both)

- Pollard, T., Moody, B. E., Lehman, L., Gow, B., Fernandes, C., Xie, C., Johnson, A.,
  Mark, R. G., & Heldt, T. (2026). PhysioNet as a global platform for biomedical research.
  Nature Health. https://doi.org/10.1038/s44360-026-00096-z

### Looked at and not used

- RobustPDx (mouse and keyboard tasks, Figshare, CC0, https://doi.org/10.6084/m9.figshare.32099416):
  cursor positions saved about twice a second, too slow to contain a 4–6 Hz tremor.

## Pretrained models

- None. Both models (the tremor detector and the tremor corrector) were trained by us.

## AI service inside the product

- Claude API (Anthropic), model Claude Sonnet 5.5 (`claude-sonnet-5-5`), effort `low`,
  streamed: the in-app assistant. It receives only the session's summary numbers, never raw
  pointer movement. https://docs.claude.com

## AI tools used while building

- Claude Code (Anthropic): planning, writing and testing most of the code.
- ChatGPT (OpenAI): drafting the write-up and the video script.
- The ui-sdk agent skill (Vercel Labs): the library's own instructions for AI assistants,
  used during the interface redesign.

## Libraries

Exact versions are pinned in `requirements.txt`.

- NumPy, https://numpy.org (arrays and maths)
- pandas, https://pandas.pydata.org (installed with the project's requirements)
- SciPy, https://scipy.org (band-pass filters, frequency spectra)
- scikit-learn, https://scikit-learn.org (the detector: HistGradientBoostingClassifier and
  Regressor, permutation importance)
- joblib, https://joblib.readthedocs.io (saving the trained detector)
- threadpoolctl, https://github.com/joblib/threadpoolctl (keeps live detector calls fast)
- PyTorch, https://pytorch.org (the corrector network, trained with the Adam optimiser)
- Matplotlib, https://matplotlib.org (all charts)
- FastAPI, https://fastapi.tiangolo.com, and Uvicorn, https://www.uvicorn.org (the local server)
- websockets, https://websockets.readthedocs.io (the server test)
- Anthropic Python SDK, https://github.com/anthropics/anthropic-sdk-python (Claude API)
- python-dotenv, https://github.com/theskumar/python-dotenv (reads the API key from `.env`)
- certifi, https://github.com/certifi/python-certifi (trusted certificates for the download)
- pytest, https://pytest.org (automatic tests)
- PyObjC (pyobjc-framework-Quartz), https://pyobjc.readthedocs.io (macOS only: reading the
  pointer and steadying the real cursor through Apple's Quartz Event Services,
  https://developer.apple.com/documentation/coregraphics/quartz_event_services)
- ui-sdk web components, `@ui-sdk/web` 0.1.0-beta.1 (Vercel Labs, Apache-2.0),
  https://ui-sdk.dev, copied into `web/vendor/ui-sdk/` with its licence

## Fonts (all SIL Open Font License 1.1, stored in `web/fonts/` with their licences)

- Bricolage Grotesque (Atelier Triay), https://github.com/ateliertriay/bricolage
- Instrument Sans (Instrument), https://github.com/Instrument/instrument-sans
- OpenDyslexic (Abbie Gonzalez), https://opendyslexic.org

## Methods and papers

- One Euro filter, used as a baseline: Casiez, G., Roussel, N., & Vogel, D. (2012). 1€ Filter:
  A Simple Speed-based Low-pass Filter for Noisy Input in Interactive Systems. CHI 2012.
  Reference code: https://github.com/casiez/OneEuroFilter (our version was written from scratch
  following it).
- Kalman filter, used as a baseline: Kalman, R. E. (1960). A New Approach to Linear Filtering
  and Prediction Problems. Journal of Basic Engineering, 82(1).
- Gradient boosting (the detector): Friedman, J. H. (2001). Greedy function approximation: a
  gradient boosting machine. Annals of Statistics, 29(5).
- Permutation importance: Breiman, L. (2001). Random Forests. Machine Learning, 45.
- Adam optimiser (training the corrector): Kingma, D. P. & Ba, J. (2014). Adam: A Method for
  Stochastic Optimization. arXiv:1412.6980.
- Dilated causal convolutions (the corrector's layers): van den Oord, A. et al. (2016). WaveNet:
  A Generative Model for Raw Audio. arXiv:1609.03499.
- Minimum-jerk reaching (the computer-made mouse movement): Flash, T. & Hogan, N. (1985). The
  coordination of arm movements: an experimentally confirmed mathematical model. Journal of
  Neuroscience, 5(7).
- Fitts's law (reach time vs distance and target size): Fitts, P. M. (1954). The information
  capacity of the human motor system in controlling the amplitude of movement. Journal of
  Experimental Psychology, 47(6).
- Bootstrap (uncertainty ranges): Efron, B. (1979). Bootstrap Methods: Another Look at the
  Jackknife. Annals of Statistics, 7(1).
- Related work: White, R. W. & Horvitz, E. (2019). Population-scale hand tremor analysis via
  anonymized mouse cursor signals. npj Digital Medicine. https://doi.org/10.1038/s41746-019-0171-4
- W3C Pointer Lock (the "Lower sensitivity" mode): https://www.w3.org/TR/pointerlock-2/
- Web Speech API (the "Read aloud" button):
  https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
- British Dyslexia Association, "Dyslexia friendly style guide" (the "Easier-to-read text" switch).

## Work done before the hackathon

- Only dataset research. No code written before the hackathon is in this repository: the two
  files first planned for reuse (the data download script and the classic filters) were
  rewritten from scratch during the weekend.
