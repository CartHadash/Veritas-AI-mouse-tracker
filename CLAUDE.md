# Context and rules for every AI assistant working in this repository

Read this whole file before doing anything. Then read, in this order:

1. `docs/COMPETITION_RULES.md`: what the hackathon allows and what judges score.
2. `docs/PROJECT_PLAN.md`: what we are building, who owns which folder, the contracts.
3. `STATUS.md`: where things stand right now.
4. Your lane's guide: `BUILD_GUIDE_BUILDER.md` **or** `BUILD_GUIDE_LEADER.md`. Ask your
   human which one if they have not said.
5. `docs/DATASETS.md` and `docs/REUSED_CODE.md` before touching data or old code.

## The project in three lines

A tremor-aware pointer assistant for the Veritas AI hackathon (AI + Health track,
deadline Sun 15 Nov 23:59 US Eastern = Mon 16 Nov 05:59 CET). Two trained models: one
**detects** tremor in mouse movement, one **corrects** it. Around them: a local web app
with a live demo, a session summary, and a Claude-powered assistant that explains the numbers.

## Who you are working with

High school students who know some Python and a little C++, with very little machine-learning
experience. One of them must be able to explain every part of this project to a panel of AI
researchers. So:

- **Explain before you do.** Before each step, say in two or three plain sentences what you
  are about to do and why. No jargon without a one-line explanation the first time.
- **When a choice is theirs, stop and ask**, using the format under "Asking your human".
- **Write simple, commented code.** A clear 20 lines beats a clever 5. No extra frameworks,
  config systems or abstractions.
- **After each step, add a short plain-language entry to `docs/EXPLAINED.md`**: what this
  part does, why we chose it, and how we know it works. This file is how the team learns
  the project well enough to defend it.

## Hard rules

1. **Stay in your lane.** Edit only the folders your lane owns (table in
   `docs/PROJECT_PLAN.md`). Need something elsewhere? Write it under "Requests" in
   `STATUS.md` and tell your human.
2. **Do not copy code from the old repository** (`mouse-tracking-model`) or from memory of
   it. Only the two files in `docs/REUSED_CODE.md` are allowed.
3. **Never invent a number.** Every figure in any `.md` file must come from a script's
   output, and the entry must name the script. If something failed or was not run, say so.
4. **Split by subject.** A person whose recordings are in the training data must never
   appear in validation or test data. Fix the random seed and save the split to a file.
5. **Tune on validation, report on test.** The test subjects are used once, at the end of
   each model version, never for choosing settings.
6. **Always compare with a baseline**, and always report missed cases and false alarms
   separately for the detector.
7. **Data stays out of git.** Never commit `data/`, `local_logs/`, `.env`, or anything over
   a few MB. Saved model weights must be small (aim under 2 MB each).
8. **The API key lives only in `.env`** (ignored by git) or the shell environment. Never
   write it in code, a commit, a log, `STATUS.md` or a chat message.
9. **Public or synthetic data only.** Do not train on, or report results from, mouse data
   recorded from any real person. The app may *display* the current user's own live
   movement and keep it in `local_logs/` on their laptop.
10. **No medical claims.** The detector flags tremor-like movement; it does not diagnose.
    The assistant never gives medical advice. Wherever results are shown to a user or a
    judge, the line "This project is a prototype and is not medical advice." appears.
11. **A model that runs live must be causal** (it may use only current and past samples)
    and fast (well under 8 ms per sample on the laptop's CPU).
12. **Cite as you go.** The moment you use a new dataset, library, tutorial, pretrained
    model or AI tool, add it to `docs/SOURCES.md`.
13. **Do not edit `README.md`** until the team leader says the write-up phase has started.

## Git rules

- Run `git pull` before starting any work session.
- **Small fixes** (a typo, a one-line bug) go straight to `main`.
- **Any big addition** (a new module, a model, a page, anything over about 50 lines) goes
  on its own branch, named `lane/short-description`, for example
  `builder/tremor-library` or `leader/assistant`.
- **Push the branch immediately** when the addition works, even if unpolished, so teammates
  can see it. Do not sit on unpushed work.
- **Then merge it into `main` yourself, but only when all of these are true:**
  1. the code runs from a clean start (you ran it, not assumed it);
  2. nothing that worked on `main` before is broken (re-run the earlier steps' checks);
  3. `STATUS.md` and any affected `.md` files are updated in the same branch;
  4. you touched only your lane's folders.
  If any is false, leave the branch pushed and unmerged, and say why in `STATUS.md`.
- Merge with `git checkout main && git pull && git merge --no-ff <branch> && git push`.
  If there is a conflict in a file your lane does not own, stop and ask your human.
- Commit messages say what changed and why, in plain words.
- Never force-push. Never rewrite history on `main`.

## Keeping the instructions up to date (every agent, every session)

These `.md` files are the team's shared memory. Stale instructions cost hours. So:

**At the end of every work session, before your final commit:**

1. **`STATUS.md`**: update "Right now" for your lane; add what you finished to "Done";
   put any new real numbers under "Results so far" with the script that produced them;
   record decisions, and anything that did not work.
2. **Your build guide**: tick the checkbox of each finished step (`- [x]`). If you did a
   step differently from what the guide says, **edit the step** so it describes what was
   actually done, and add one line starting `Changed:` explaining why. If you discovered a
   step is unnecessary or a new one is needed, remove or add it.
3. **`docs/PROJECT_PLAN.md`**: if a contract, a folder, an owner or a decision changed,
   update it. Contract changes must be agreed with the other lane first.
4. **`docs/EXPLAINED.md`**: add the plain-language explanation of what you built.
5. **`docs/SOURCES.md`**: add anything new you used.
6. **This file (`CLAUDE.md`)**: if you learned something every agent needs to know (a
   command that must be run a certain way, a trap you fell into), add it under
   "Things we learned the hard way" below. Keep it short.

**Rules for editing these files:**

- Fix what is wrong; do not just append. A reader should never find two instructions that
  disagree. If you replace an instruction, delete the old one.
- Never delete another lane's notes or a recorded result. If you think one is wrong, add a
  line under "Requests" in `STATUS.md`.
- Never change the "Decisions" table in `PROJECT_PLAN.md` or anything in
  `COMPETITION_RULES.md` without the team leader saying so.
- Before you start a session, re-read `STATUS.md` and your guide: another agent may have
  changed them since you last looked.

## Asking your human

When a step says **DECISION**, or you hit a choice that changes what gets built, stop and
ask like this:

> **Decision needed: [short name]**
> What this is about: [one or two sentences, no jargon]
> Option A: [what it is] → [what it means for us]
> Option B: [what it is] → [what it means for us]
> I recommend [A/B] because [one sentence].
> If you are unsure, say "go with your recommendation".

Do not ask about things the guide or `PROJECT_PLAN.md` already decides. Do not ask
permission for routine work inside your lane.

## Commands (keep this list current)

Windows (PowerShell), the builder's machine:

```powershell
python -m venv .venv                      # once
.venv\Scripts\Activate.ps1                # every new PowerShell window
python -m pip install -r requirements.txt # after requirements change
python scripts\download_data.py           # once; 1.5 GB into data\
```

macOS, the team leader's machine and the demo machine:

```bash
python3 -m venv .venv                     # once
source .venv/bin/activate                 # every new terminal window
python -m pip install -r requirements.txt # after requirements change
python scripts/download_data.py           # once; 1.5 GB into data/
```

(Each lane adds its own commands here as they come into existence.)

## Things we learned the hard way

- **The team uses two operating systems** (builder: Windows; leader and demo: macOS).
  Shared code must run on both: `pathlib` paths, `encoding="utf-8"` on every text file,
  no worker processes outside `if __name__ == "__main__":`, model weights saved from the
  CPU. Find out which machine you are on before running any command.

- PADS text files have 7 columns, not the 6 the official page describes; time is first.
- TremorDB files are plain numbers, one per line; the `wfdb` library cannot read them.
- On macOS, asking where the pointer is needs no permission; listening to mouse events or
  moving the real cursor needs the Accessibility permission for the app that launched Python.
- PhysioNet's own zip download was very slow; the download script uses PhysioNet's public
  Amazon mirror instead.
