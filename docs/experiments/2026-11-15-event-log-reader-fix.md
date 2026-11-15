# S014l: event-log reader fix (KI-24)

Engineering milestone in open-lab-simulation (commit `e277ba1`). It changes no
rubric, re-scores nothing and edits no recorded file.

## What was wrong

`canonical_json` writes U+0085, U+2028 and U+2029 raw (`ensure_ascii=False`).
Python's `str.splitlines()` treats each as a line break, so every Simulation
reader that used it cut an intact event in two. In S014i-001 cell `s41-r2-c`
the model tested `text.stats` with U+2028/U+2029, and the frozen
`verify_archive` reported the sound record as `INVALID_RECORD`.

## What changed

`contracts.jsonl_lines` splits on `"\n"` only. It replaces `splitlines()` in
`archive.verify_archive`, the recorder's append path, the campaign ledger
(`benchmark.read_ledger`), the provider ledger and its per-run mirror
(`provider-ledger.jsonl`), the artifact index and the events reader in
`artifacts`, the supervisor's recovery and resume paths, and
`benchmark_analysis.analyse_archive`. One supervisor reader also lacked
`encoding="utf-8"` and now has it. The three remaining `splitlines()` calls
read subprocess output or a GPU query, where every separator is a real break.
The Window splits bytes on `\n` and was not changed.

## Tests

- New `tests/test_line_separators.py` (6 tests): a scripted run whose output,
  `text.stats` input and workspace file hold U+2028, U+2029 and U+0085
  verifies and analyses; the recorder appends to such a log; the campaign
  ledger, the provider ledger, its mirror and the artifact index read entries
  holding them; and a static check finds no `splitlines()` in a JSONL reader.
- Before the fix (helper added, readers unchanged) four of the six failed:
  `verify_archive` reported `line 7: not JSON` and 38 more problems, the
  recorder refused to append ("invalid event log"), a ledger raised
  `JSONDecodeError`, and the static check listed 11 call sites.
- After the fix: Simulation `ruff check .` passed; 366 tests passed
  (360 before plus 6).

## The `s41-r2-c` archive (reported, not re-scored)

Read-only check of `runs/s014i-001-s41-r2-c/run-20261115t095821z-f2dc89`:

| Reader | Problems |
| --- | --- |
| Frozen source (`8301244`) | 236 (first: `line 125: not JSON`) |
| Fixed source (`e277ba1`) | 0 |

The log has 296 events and contains 22 U+2028 and 22 U+2029 characters and no
U+0085. Its SHA-256 (`6e73be44…077b1a`) was the same before and after the
check. All 24 S014i-001 archives verify with the fixed reader.

S014i-001 stays **INCONCLUSIVE** as registered and reported in S014j; its
records, reviews and dataset were not modified. Because the runtime source
changed, the s014i-001 manifest's source check now reports a mismatch; its
report remains bound to the frozen source it was produced on.
