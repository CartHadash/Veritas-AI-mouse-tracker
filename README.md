# TAG Pointer

**Track:** Health
**Team:** Names on the submission form

**This project is a prototype and is not medical advice.**

<!-- Demo video: add the link here once it is recorded (script: docs/VIDEO_SCRIPT.md). -->

## The problem

Controlling a computer mouse may be challenging for someone with Parkinson's disease or essential tremor who uses a laptop at home owing to the involuntary hand movements that make clicking a checkbox, closing a window or selecting a small target difficult. Conventional filtering methods often trade-off diminished tremor for responsiveness which may make precise digital interaction difficult.

## What we built

TAG-Pointer is a mouse stabilisation tool based on a trained model that understands tremors. Users move the mouse as usual, yet the system detects involuntary tremor-like motion and corrects the pointer trajectory in real time.

## What we added

We have developed Click Freeze, which improves click performance when using high simulated tremor values, providing session performance summaries and focusing on user privacy by providing local tracking. Mouse data is accessed by the assistant for summary statistics.The assistant sees only summary statistics but never raw mouse movement.

## How it works

Data: Tremor data from public sources (PADS/TremorDB) and synthetic mouse data. As there is no publicly available data that can be directly used in this scenario, real-world tremor data from wrist/fingertips was mapped to simulated mouse. 
Detection: Gradient boosting is used to identify likely tremor motion, and, besides, it also analyses the 19 explainable traits over the past 2.56 seconds
Correction: A neural network uses the previous 0.64 seconds of cursor movement to estimate and remove tremor. Rather than the Corrector modifying all mouse movements, the Corrector is activated/deactivated by Detector v2. 
Application: Real time pointer smoothing, Click Freeze, session analytics and AI assistant.

## Results

**Detector.** Accuracy alone misleads, so missed cases and false alarms are shown apart:

| Detector | Missed cases | False alarms | Accuracy |
|---|---|---|---|
| Baseline: always "no tremor" | 100.0% | 0.0% | 74.5% |
| Baseline: frequency rule | 14.8% | 59.0% | 52.3% |
| **Ours** | **12.9%** | **27.1%** | **76.5%** |

Across groups it is close: missed cases were 12.9% under 60, 12.7% at 60 to 69 and 13.2% at
70 and over; 10.4% for women and 14.8% for men. With 72 test people the 95% range for missed
cases is 9.7% to 18.4%.

**Corrector.** The network alone removed 88% of the tremor with no measurable lag; the classic
One Euro filter removed 49% and trailed the hand by 20 ms. As a person sees it on the demo
page, the shake left on the cursor was:

| Method | Shake left (px) |
|---|---|
| Baseline: no filter | 7.91 |
| Baseline: One Euro | 3.39 |
| **Ours (network + smoothing, as in the app)** | **2.56** |

**Where it fails, and why we think so.**
- **Small tremor is missed:** 34.2% of tremor under 3 px, against 2.9% over 10 px. It is hidden
  under deliberate movement tens of pixels large.
- **Some "false alarms" look exactly like tremor.** They are 41.7% on tasks where the patient
  moved on purpose, against 19.5% at rest; our labelling rule probably left real tremor
  unmarked there. The chart shows the most confident one, a strong, regular 5 Hz shake.

  ![A false alarm that looks like tremor](evaluation/results/failures/detector_false_alarm_1.png)
- **It lags a moving hand.** The smoothing that calms the cursor trails the hand by 72 ms.
  While reaching with medium tremor the cursor ends up further from the intended path than
  with no filter (7.38 px against 6.08 px).
- **No person with tremor has tried it**, and the mouse movement is computer-generated, so
  real-world results will probably be weaker.

More failures with charts: [failures.md](evaluation/results/failures/failures.md).

## What we'd do next

1. Test it with people who have tremor. Nothing we measured replaces that.
2. Retrain the detector to be stricter during fast deliberate movement, where most false
   alarms happen. Changing the cut-off alone did not help; we tried it.

## Run it

```bash
python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn server.main:app          # then open http://127.0.0.1:8000
```

No dataset download is needed to run the app. Windows and rebuilding the results:
[docs/RUNNING.md](docs/RUNNING.md). Every part explained in plain words:
[docs/EXPLAINED.md](docs/EXPLAINED.md).

## Sources

The full list with every paper and licence is in [docs/SOURCES.md](docs/SOURCES.md).

- **Datasets:** PADS, Parkinsons Disease Smartwatch dataset v1.0.0, PhysioNet,
  https://doi.org/10.13026/m0w9-zx22 (CC BY-NC-SA 4.0). Effect of Deep Brain Stimulation on
  Parkinsonian Tremor (TremorDB), PhysioNet, https://doi.org/10.13026/C2D097 (ODC-By 1.0).
- **Pretrained models:** none. Both models were trained by us.
- **AI service in the product:** Claude API (Anthropic), model `claude-sonnet-5-5`,
  https://docs.claude.com.
- **AI tools used while building:** Claude Code (Anthropic) for planning, writing and
  testing most of the code; ChatGPT (OpenAI) for drafting the write-up and video script.
- **Libraries:** [NumPy](https://numpy.org), [pandas](https://pandas.pydata.org),
  [SciPy](https://scipy.org), [scikit-learn](https://scikit-learn.org),
  [Matplotlib](https://matplotlib.org), [PyTorch](https://pytorch.org),
  [FastAPI](https://fastapi.tiangolo.com), [Uvicorn](https://www.uvicorn.org),
  [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python),
  [python-dotenv](https://github.com/theskumar/python-dotenv),
  [certifi](https://github.com/certifi/python-certifi), [pytest](https://pytest.org),
  [PyObjC](https://pyobjc.readthedocs.io), [ui-sdk](https://ui-sdk.dev) web components.
- **Fonts:** [Bricolage Grotesque](https://github.com/ateliertriay/bricolage),
  [Instrument Sans](https://github.com/Instrument/instrument-sans) and
  [OpenDyslexic](https://opendyslexic.org), all under the SIL Open Font License.
- **Methods:** One Euro filter (Casiez, Roussel and Vogel, 2012,
  https://github.com/casiez/OneEuroFilter), used as a baseline; gradient boosting (Friedman,
  2001); dilated causal convolutions (van den Oord et al., 2016, arXiv:1609.03499); related
  work on tremor in cursor movement (White and Horvitz, 2019,
  https://doi.org/10.1038/s41746-019-0171-4).

**This project is a prototype and is not medical advice.**
