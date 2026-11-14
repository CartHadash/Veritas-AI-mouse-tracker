# Where our models fail (step 9, updated for the final models)

All examples and counts come from `python evaluation/find_failures.py` on **test** people, with
the models the app uses: detector v2 (cut-off 0.155) and corrector v4 (smoothness penalty 0.5)
gated by detector v2. Exact figures are in `failure_facts.md`, charts in this folder. The
explanations are our interpretation after looking at each chart; they are labelled as such.

(The first version of this analysis, on detector v1 and corrector v1, found the same patterns.)

This project is a prototype and is not medical advice.

## Detector: missed cases (tremor called "no tremor")

On test, 122 of 944 tremor windows are missed (12.9%).

**Examples** (`detector_missed_1.png` to `_3.png`), all Parkinson's patients at rest:
1. tremor of only 0.4 px, added to movement tens of pixels large;
2. a window that is calm for the first 1.8 seconds, followed by a burst of about 20 px at the
   very end (average size 6.0 px over the window);
3. tremor of 1.0 px, while the hand is moving and doing a deliberate look-alike movement for
   62% of the window.

**Our explanation.**
- *Tiny tremor (examples 1 and 3).* The tremor rule marks a segment by the **wrist sensor**: it
  is stronger than in 95% of healthy people at rest, whose resting wrists are very still. After
  conversion to pixels, some marked tremors are well under one pixel: invisible on a screen and
  buried under deliberate movement. The detector is not wrong to see "no visible tremor" there.
  The pattern supports this: missed cases are 34.2% of mild tremor (under 3 px), 11.0% of medium
  and only 2.9% of strong (over 10 px).
- *Tremor that comes and goes (example 2).* Each 2.56 s window gets the label of its whole
  10.24 s recording. If the tremor comes and goes, a window can be mostly calm and still be
  labelled "tremor". Live, the detector would catch the burst a moment later, once more of it
  is inside its 2.56 s window.

**What it means for the user:** the tremors we miss are mostly too small to shake the cursor
noticeably, or short bursts that are caught a moment later.

## Detector: false alarms ("tremor" when the label says none)

On test, 750 of 2,764 no-tremor windows are false alarms (27.1%).

**Examples** (`detector_false_alarm_1.png` to `_3.png`): all three are patient segments from
**action** tasks (Parkinson's, essential tremor, other movement disorder) that the rule did not
mark, carrying 10-26 px of 3-12 Hz movement. Example 1 shows a strong, very regular 5 Hz wave
with a sharp spectrum peak and a second peak near 10 Hz, which looks exactly like tremor.

**Our explanation: many of these are probably real tremor that our labelling rule left
unmarked.** For action tasks, the rule compares a segment with healthy people *moving on
purpose*, which sets a very high bar (needed so deliberate movement is not called tremor).
Real tremor during action tasks can fall under that bar and is then labelled "no tremor".
Evidence:
- false alarms are highest for segments from action tasks (41.7%) and lowest for rest (19.5%)
  and synthetic movement with nothing added (10.0%);
- the unmarked patient segments that cause false alarms carry much more 3-12 Hz movement
  (median 2.64 px) than the ones correctly passed (median 0.67 px).

So part of our "false alarm" rate is really a labelling limitation, not a detector error.
We fixed the rule before training and do not change it after seeing results, so we report
the numbers as they are and explain this.

**Look-alike movement also causes false alarms**, as designed: windows where more than 30% of
the time is a deliberate wiggle, circle or zig-zag get 34.4% false alarms, versus 21.0% for
the others.

## Corrector: sequences where it does worse

Our system is further from the intended path than the *better* of no filter and One Euro in
381 of 930 test sequences, and in 33 of the 236 with marked tremor. This is a strict
comparison, because it takes whichever of the two was best for each sequence; on sequences
without marked tremor the gate is mostly closed, so our output is close to the raw cursor.

**Examples** (`corrector_worse_1.png`, `_2.png`): a Parkinson's patient's and a healthy
person's action-task segment, neither marked as tremor, carrying 17 and 12.5 px of irregular
3-12 Hz movement. Average distance to the intended path: ours 12.9 / 10.4 px, no filter
13.0 / 10.7 px, One Euro 4.6 / 4.6 px.

**Our explanation.** This movement is not a steady rhythm, so the detector keeps the gate
almost closed (average gate 0.02 and 0.04) and our system leaves the cursor almost untouched.
That is the design: a steady hand should not be smoothed. One Euro smooths everything, so it
wins on irregular shaking like this, at the cost of lag everywhere else (40 ms; and on the
sequences without marked tremor it is far further from the path than ours: 12.95 vs 1.85 px).

## The patterns in one paragraph

Most detector "misses" are tremors under a few pixels that hardly move the cursor, or short
bursts the detector catches a moment later. Many "false alarms" come from action tasks, where
our fixed labelling rule probably left real tremor unmarked, plus deliberate look-alike
movement. The corrector loses to One Euro mainly on irregular shaking that the detector
(correctly) does not call tremor, so its gate stays closed. Two possible next steps: label
tremor with a rule that does not depend on task type, decided before retraining; and let the
gate react to strong irregular shaking as well.
