# ADR-0022: Strategic reset — build the Habitat before more test campaigns

Status: Accepted (owner direction, 2026-11-16). Amends the experimental-purpose
rules in AGENTS.md, the expansion gates of ADR-0013 and the per-capability
real-model check of ADR-0017. Retires the S011b/S011c endurance programme and
other pending campaign milestones. It does not delete any record.

## Context

S001–S011a built a working laboratory:

- versioned worlds with discoverable capabilities;
- a supervised runtime that local and hosted models can drive;
- an independent hash-chained recorder;
- checkpoints and recovery;
- resource limits;
- a rootless-container tier;
- a read-only Window.

Most of the recent work, however, has been registrations, comparison
campaigns and reliability protocols run in a world with eleven utilitarian
tools and nothing to discover. Every hosted unguided run (S011p, S011a ×3)
ended the same way: look around, find nothing, stop.

The owner judged that the development process had become the experiment. The
original purpose is still the destination: an AI in a rich computational
universe, under an existential premise, with no further instructions, freedom
to choose its objectives, persistent memory, time, and an independent
observer.

## Decision

1. **Active development follows the Habitat roadmap.** The next milestones are
   vertical slices (S015 onward). Each one adds a real new freedom for the
   inhabitant: inspect and improve its own files, run its own programs, make and
   reuse skills and tools, interact with a world that has open-ended phenomena,
   and manage its own time and continuity. Habitat v1 is defined in
   [docs/habitat/HABITAT_V1.md](../habitat/HABITAT_V1.md).
2. **The following are retired from the active queue:**
   - S011b and S011c (12- and 72-hour endurance);
   - further 24-cell or 72-cell model-comparison campaigns;
   - repeated capability benchmarking;
   - S014k (provider comparison view);
   - new registration and bookkeeping machinery that has no immediate use for
     the world.

   Deferred, not cancelled: S010c (Window comparison), S006f (world images,
   Linux, brokered networking), S007b/S008a/S008b (vision, audio, media). They
   return when a Habitat slice needs them.
3. **Evidence for a new capability is an engineering demonstration.** Each
   capability needs unit and integration tests, plus security and isolation
   tests if it executes code. It also needs one preserved end-to-end acceptance
   demonstration: the real supervisor and world, with a scripted model by
   default, or one bounded real-model check when a model is genuinely needed.
   The ADR-0017 requirement of a real-model discovery/use check for every
   capability is relaxed to "when useful, and approved". No statistical
   campaign is required to show that a capability works.
4. **Formal campaigns are reserved** for a mature habitat and a specific
   scientific question. The first is S012, the philosophical experiment, which
   is now gated on Habitat v1 and not on endurance runs.
5. **Unchanged:**
   - the three-repository architecture and boundaries;
   - the container requirement for agent-supplied code;
   - the observer and recorder rules;
   - honesty rules;
   - hosted inference only with explicit owner approval;
   - completed records stay as written.

## Consequences

- "Run next session" now leads to S015 and its successors, not to endurance or
  comparison work.
- Some existing documents (AUTONOMY_AND_EXPERIMENTAL_READINESS.md, ADR-0013 and
  ADR-0017 gates) describe the old campaign gates. They are retained as
  history. Where they conflict with this ADR, this ADR governs.
- Experiments run during Habitat development are demonstrations, not studies.
  Reports must not present them as autonomy evidence.
