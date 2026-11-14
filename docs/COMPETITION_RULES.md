# Competition rules that affect our work

A summary, in our own words, of the Veritas AI International High School Hackathon 2026
"Hacker Guide" and "Project Briefs". If anything here seems to disagree with the official
documents, the official documents win. Ask the team leader.

## Dates

| | US Eastern (official) | Central European Time |
|---|---|---|
| Hacking started | Sat 14 Nov, 00:00 | Sat 14 Nov, 06:00 |
| **Submissions close** | **Sun 15 Nov, 23:59** | **Mon 16 Nov, 05:59** |
| Finalists announced | Wed 18 Nov | |
| Live finals (5 min + questions) | Sat 21 Nov, 11:00 | Sat 21 Nov, 17:00 |

You can resubmit as often as you like; judges see the latest version. The briefs advise
submitting a first version a few hours before the deadline.

## The rules (all eight)

1. **Team:** 1–3 high school students; everyone listed must have contributed.
2. **Build during the weekend.** All project work happens between the start and the
   deadline. Learning tools and browsing datasets beforehand is fine, but "you can't extend
   a project you built before the hackathon". See `REUSED_CODE.md` for how we handle this.
3. **AI must be central.** The project must use AI or machine learning to do its *main*
   job. A normal app built with AI coding tools "doesn't count on its own".
4. **Allowed:** public datasets, pretrained models, AI APIs, open-source libraries, tutorial
   code, coding assistants and chatbots. **All must be cited.** The team must understand
   every part of the project and be able to explain it to judges.
5. **Not allowed:** submitting someone else's project; collecting anyone's personal
   information without permission. "Stick to public or synthetic data."
6. **One project, one track.**
7. **Disclaimer:** health projects must say they are a prototype and not medical advice.
8. **Honest results:** report what you actually got, including weak results.

## Our track: AI + Health

Challenge: *build an AI tool that helps one specific person catch a health problem sooner,
or manage an ongoing one better.* Ours is the "manage an ongoing one better" half, entered
as "Our own idea" (brief section 4.1.4).

The Health brief requires:

- **Name the user** and explain how they would use the tool.
- **Report missed cases (false negatives) and false alarms (false positives) separately**,
  not just overall accuracy.
- Include this exact line in the write-up:
  **"This project is a prototype and is not medical advice."**
- **Use public datasets only.** No real patient records, even ones we could access.

Health judges "pay extra attention to how clearly you identify your user, how honestly you
report missed cases and false alarms, and whether you checked that your model works equally
well across groups such as age, sex".

## What every project must show

1. **Who is it for?** One specific user and the moment they would reach for the tool.
2. **What goes in, what comes out?** A real input producing a result.
3. **Does it beat a simple baseline?** Report the baseline's score next to the model's.
4. **Where does it fail?** At least one example the model gets wrong, with our best
   explanation of why.

All results must come from **test data the model did not see during training**. Results
that look too good usually mean test data leaked into training; judges score an honest,
modest result higher than an unexplained high one.

## How projects are scored

| Criterion | What judges look for | How to show it |
|---|---|---|
| Technical quality | It works, the approach is sound, it was tested fairly | Baseline comparison, unseen test data, shown failures |
| Impact | A real problem for real people | Who it helps and what changes for them |
| Creativity | A fresh approach, not a repeated tutorial | A known technique on an unusual dataset, question or user |
| Clarity | Understandable in two minutes | Clear demo, concise write-up, one main takeaway |

Round 1 is reviewed blind (reviewers do not see names or schools). Finalists present live.
Likely finals questions: "How do you know it works?", "What would cause it to fail?",
"Who would use this?"

## What we must submit

| Item | Required | Notes |
|---|---|---|
| Code | Yes | This GitHub repository; must open without signing in |
| Write-up | Yes | About one page, the official template. Ours is `README.md` |
| Demo video | Optional, recommended | Up to 2 minutes; YouTube unlisted or Google Drive link |
| Team details | Yes | Track, and each member's name, email and school (on the form) |
| Credits | Yes | Every dataset, pretrained model, tutorial and AI tool, with links |

Before submitting, open every link in a private browser window.

### Write-up template (official; goes in README.md at the end)

```
# Project name
**Track:** Health / Finance / Climate / Languages
**Team:** names
## The problem
Who has this problem, and why does it matter? (2-3 sentences)
## What we built
What goes in, what comes out, and how someone would use it.
## What we added
If you started from a suggested project: which one, and what you added
or changed. Otherwise, write "Our own idea".
## How it works
Data: which dataset, how many examples, how we cleaned it.
Model: what we used and why.
## Results
Our baseline scored X. Our model scored Y on held-out test data.
Where it fails, and why we think so.
## What we'd do next
One or two concrete next steps with more time.
## Sources
Datasets, pretrained models, tutorials and AI tools used, with links.
```

### Demo video structure (official suggestion)

| Part | Length | Show |
|---|---|---|
| The problem | ~15 s | Who it is for and why it matters |
| The demo | ~60 s | A real input going in and the result coming out |
| How it works | ~30 s | Data, model, and how it compares with the baseline |
| Next steps | ~15 s | One limitation and what we would do next |

## Other things worth knowing

- **No technical help from mentors** during the weekend; only submission problems.
- If an AI API is used, judges care most about **what we built around it**: our data, our
  evaluation, our interface.
- Advice from the guide: stop adding features about six hours before the deadline; if
  stuck on one problem for 30 minutes, simplify or switch approach.
- Awards include Best Beginner Build, Best AI for Good and Judges' Choice.
