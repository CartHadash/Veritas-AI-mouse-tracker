# Demo video script (2 minutes)

Written by the leader's agent, Sun 15 Nov, from `docs/COMPETITION_RULES.md` (the official
video structure and the scoring table) and `evaluation/results/RESULTS.md`. Every number
below is copied from `RESULTS.md`; the line under each part says which table. If a number in
`RESULTS.md` changes, change it here too.

The limit is **2 minutes**. The words to speak are about 285, which is about 1 minute 55 at
a calm speaking pace. Read it aloud with a timer before recording; what to cut if it runs
long is at the end.

## What the judges score, and where the video earns it

| Criterion | What they look for | Where this script shows it |
|---|---|---|
| Impact | A real problem for a real person | Part 1: one named user and the moment it hurts |
| Clarity | Understandable in two minutes | One idea per part; the same two dots on screen throughout |
| Technical quality | Works, sound, tested fairly | Part 3: unseen test people, baseline next to ours, missed cases and false alarms separately |
| Creativity | A fresh approach | Part 3: no dataset existed, so we built one from real tremor |

Health judges also look for an honest limit and the disclaimer: Part 4.

## The script

### Part 1. The problem (0:00 to 0:15)

**On screen:** the Practice tab, demo tremor on at Strong, filter on "No filter". The cursor
shakes and misses the small checkbox target twice.

**Say:**
> Someone with Parkinson's or essential tremor opens their laptop, and the pointer shakes.
> The small things are the hardest: a checkbox, the cross that closes a window. We built a
> tool that steadies the cursor for them.

### Part 2. The demo (0:15 to 1:15)

**On screen, in this order:**
1. Point at the "Demo mode" banner while saying the first sentence.
2. Switch the filter from "No filter" to "Our model". Let the grey dot and the dark dot be
   seen apart for two seconds.
3. Click three targets (a checkbox, a folder, a close button).
4. Point at the tremor meter and its live graph.
5. Run the fair test, sped up to about five seconds in editing, and hold on the result card.
6. Cut to the clip already recorded: "Steady cursor everywhere" in another app.
7. Open the assistant, tap "Explain my summary", show the answer and the reminder under it.

**Say:**
> This is TAG Pointer. None of us has tremor, so the shaking you see is replayed from
> public recordings of patients. The grey dot is the raw movement. The dark dot is what our
> model shows.
>
> These targets are things people really click, and a click only counts if you press and
> release on the target.
>
> The meter is our first model, the detector. It scores the last two and a half seconds of
> movement, and the correction switches on only when it sees tremor, so a steady hand is
> left alone.
>
> The fair test gives ten targets without our model and ten with it. Here is the result.
>
> One switch applies the same correction to the real cursor in every app.
>
> And the assistant explains the session in plain words. It sees only summary numbers, and
> it never gives medical advice.

Do not say a number for the fair test: it is whatever the recording shows. Read the two
numbers off the result card if there is time.

### Part 3. How it works (1:15 to 1:45)

**On screen:** the "How it works" tab with its moving picture for the first sentence, then
the chart `evaluation/results/figures/tremor_library_examples.png`, then the two numbers as
large captions.

**Say:**
> No public mouse recordings of people with tremor exist. So we took real tremor from 484
> people in two public datasets and added it to computer-generated mouse movement, split by
> person, so the people we tested on were never seen in training.
>
> On those people our detector missed 12.9 percent of tremor, with 27.1 percent false
> alarms. A simple frequency rule set to the same standard raised 59 percent.
>
> The shake left on screen fell from 7.91 pixels to 2.56. The classic One Euro filter
> leaves 3.39.

Sources: `RESULTS.md` "Data" (484 people, split by person); "Detector" table (12.9%, 27.1%,
frequency rule 59.0%); "On the demo page" table (shake 7.91, 2.56 and 3.39 px, test people).

**Captions:** "Missed 12.9% · false alarms 27.1% (frequency rule: 59.0%)" and
"Shake: 7.91 px → 2.56 px (One Euro: 3.39 px)". Add in small text: "test people, never
used in training".

### Part 4. Limits and next steps (1:45 to 2:00)

**On screen:** the Practice tab, a slow reach across the area so the trailing cursor is
visible, then the disclaimer as a full caption for the last three seconds.

**Say:**
> The limits. The cursor trails a moving hand by about 72 milliseconds, mild tremor while
> reaching can end up worse than no filter, and no person with tremor has tried it yet.
> That test is our next step.
>
> This project is a prototype and is not medical advice.

Sources: `RESULTS.md` "What we tried that did not work" (Steadiest 72 ms lag, test people);
"On the demo page", "Honest weakness" (mild tremor while reaching); "Limits to say out loud".

## Before recording

- [ ] Press "New session" so the numbers are only from this recording.
- [ ] Demo tremor on, level Strong. The orange "Demo mode" banner must be visible whenever
      the cursor shakes.
- [ ] Browser in full screen at normal zoom, no other tabs, no bookmarks bar.
- [ ] "Easier-to-read text" and "Larger text" off, so the page looks as in the write-up.
- [ ] The assistant's key is working: ask one question before recording, then "New session".
- [ ] Record the screen at the laptop's own resolution; speak the words afterwards over the
      picture if that is easier than doing both at once.
- [ ] No names, faces, school names or email addresses on screen or in the voice-over:
      round 1 is reviewed blind.

## If it runs over two minutes

Cut in this order; each cut loses the least:

1. The sentence about targets being "things people really click" (about 6 seconds).
2. The "Steady cursor everywhere" clip and its sentence (about 6 seconds).
3. The One Euro comparison at the end of Part 3 (about 5 seconds). Keep the frequency rule:
   a baseline next to our model is something every project must show.

Never cut: the sentence that the tremor is replayed from public recordings, missed cases and
false alarms given separately, one limit, and the last line.

## After recording

- [ ] Upload as YouTube unlisted or a Google Drive link anyone can open.
- [ ] Open the link in a private browser window to check it plays without signing in.
- [ ] Put the link in `README.md` and on the submission form.

**This project is a prototype and is not medical advice.**
