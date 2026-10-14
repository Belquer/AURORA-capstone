# How we work

## Weekly rhythm

- **One sync a week**, all three teams, 30 minutes. Notes go in `docs/meetings/YYYY-MM-DD.md`.
- Each team posts a two-line update in the week's notes: what moved, what's blocked.
- Decisions are written down in the notes the day they're made.

## Issues

- Every task is a GitHub issue with one owner, a team label (`MIP`, `MEM`, `ECE`) and an
  area label (`area:materials`, `area:production`, `area:encoder`, `area:reader-hw`,
  `area:reader-sw`, `area:business`, `area:financials`).
- A change to anything in `spec/` needs approval from both areas it connects.
- Experiments use the **Experiment** issue template. Tasks use **Task**.
- Close an issue with a link to the result, the commit or the photo.

## Experiment logs

One folder per experiment in `experiments/<short-name>/`:

```
plan.md       what we're testing, the expected result, the pass criterion
results.csv   one row per run (columns in the plan)
photos/       raw images, named date_setup_run.jpg
result.md     what happened, the number, what we do next
```

Raw data is never edited after the fact. A bad run gets a note, not a deletion.

## What not to post here (important)

This repo is **public**. Anyone can read it, and anything posted here counts as
published. AURORA is patent pending, and new inventions may be patentable too.

- If you think you've found a **new way** of doing something (a new encoding, a new
  reader trick, a new print process), **talk to Daniel before posting it**. Post it
  after we've decided whether to file on it.
- Measurements, test results, parts, code for the agreed design and meeting notes are
  fine to post.
- Never post passwords, keys, personal data or anything from a sponsor marked confidential.
- **Never post encoder code** (anything that turns audio or data into a printable disc).
  It lives in a private repo; ask Daniel for access under the NDA.

Drexel's [intellectual property policy](https://drexel.edu/provost/policies-calendars/policies/intellectual_property)
covers inventions made with university resources, including by students. Ask if
you're unsure.

## License

No license is chosen yet, so for now the contents are all rights reserved. We will
pick an open license before the end of Phase 1.
