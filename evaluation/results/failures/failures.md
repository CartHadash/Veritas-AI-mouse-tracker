# Where our models fail (step 9)

All examples and counts come from `python evaluation/find_failures.py` on **test** people
(details and exact figures in `failure_facts.md`, charts in this folder). The explanations
are our interpretation after looking at each chart; they are labelled as such.

This project is a prototype and is not medical advice.

## Detector: missed cases (tremor called "no tremor")

On test, 135 of 944 tremor windows are missed (14.3%).

**Examples** (`detector_missed_1.png` to `_3.png`): all three are Parkinson's patients at rest
whose tremor, after our pixel conversion, is only 0.2-0.4 px, added to movement that is
tens of pixels large.

**Our explanation.** The tremor rule marks a segment by the *wrist sensor*: it is stronger than
in 95% of healthy people at rest, whose resting wrists are very still. After conversion to
pixels, some of these marked tremors are well under one pixel: invisible on a screen and
buried under the deliberate movement. The detector is not wrong to see "no visible tremor"
there. The pattern supports this: missed cases are 37.0% of mild tremor (under 3 px), 12.6%
of medium and only 3.4% of strong (over 10 px).

**What it means for the user:** the tremors we miss are mostly too small to shake the cursor
noticeably.

## Detector: false alarms ("tremor" when the label says none)

On test, 747 of 2,764 no-tremor windows are false alarms (27.0%).

**Examples** (`detector_false_alarm_1.png` to `_3.png`): all three are patient segments from
**action** tasks (2 Parkinson's, 1 essential tremor) that the rule did not mark, carrying
22-26 px of 3-12 Hz movement. Example 1 shows a strong, very regular 5 Hz wave with a sharp
spectrum peak and a second peak near 10 Hz, which looks exactly like tremor.

**Our explanation: many of these are probably real tremor that our labelling rule left
unmarked.** For action tasks, the rule compares a segment with healthy people *moving on
purpose*, which sets a very high bar (needed so deliberate movement is not called tremor).
Real tremor during action tasks can fall under that bar and is then labelled "no tremor".
Evidence:
- false alarms are highest for segments from action tasks (43.5%) and lowest for rest
  (19.0%) and synthetic movement with nothing added (8.4%);
- the unmarked patient segments that cause false alarms carry much more 3-12 Hz movement
  (median 2.87 px) than the ones correctly passed (median 0.65 px).

So part of our "false alarm" rate is really a labelling limitation, not a detector error.
We fixed the rule before training and do not change it after seeing results, so we report
the numbers as they are and explain this.

**Look-alike movement also causes false alarms**, as designed: windows where more than 30% of
the time is a deliberate wiggle, circle or zig-zag get 33.4% false alarms, versus 21.6% for
the others.

## Corrector: sequences where it does worse

Our system (corrector + detector gate) is further from the intended path than the *better*
of no filter and One Euro in 506 of 930 test sequences, and in 54 of the 236 with marked
tremor. This is a strict comparison, because it takes whichever of the two was best for each
sequence; on the sequences without marked tremor the differences are usually small (gate
closed, so our output is close to the raw cursor).

**Examples** (`corrector_worse_1.png`, `_2.png`): both are Parkinson's patients' action-task
segments that were **not** marked as tremor but carry 17-18 px of irregular, spiky 3-12 Hz
movement. Average distance to the intended path: ours 12.4 / 13.5 px, no filter 13.0 /
16.7 px, One Euro 4.6 / 7.5 px.

**Our explanation.** This movement is not a steady rhythm, so the detector keeps the gate mostly
closed (average gate 0.09 in example 1) and our system leaves the cursor almost untouched.
That is the design: a steady hand should not be smoothed. One Euro smooths everything, so it
wins on irregular shaking like this, at the cost of lag everywhere else (40 ms; and on the
steady-hand sequences it is far worse than ours: 12.95 px vs 1.97 px).

## The patterns in one paragraph

Most detector "misses" are tremors under a few pixels that hardly move the cursor. Many
"false alarms" come from action tasks, where our fixed labelling rule probably left real
tremor unmarked, plus deliberate look-alike movement. The corrector loses to One Euro mainly
on irregular shaking that the detector (correctly) does not call tremor, so its gate stays
closed. Two possible next steps: label tremor with a rule that does not depend on task type,
decided before retraining; and let the gate react to strong irregular shaking as well.
