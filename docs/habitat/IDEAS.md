# Habitat ideas for later

These are preserved concepts, not commitments. Each one must earn a place in a
slice by adding real freedom for the inhabitant. See
[HABITAT_V1.md](HABITAT_V1.md) for what is active now.

## An inhabitant-owned private diary

**Concept.** A space where the inhabitant records reflections, plans, concerns
or observations that the human observer cannot read during the experiment. Its
contents would be released only after the experiment formally ends, possibly
through a cryptographic mechanism.

**Research value.** It would let us compare an agent's private record with its
public actions. It would also let us ask whether being observed changes what
an agent writes or does, and whether a promised privacy affects its behaviour.
It touches on autonomy, the observer effect, and the difference between action
and self-account.

**Conflict with the current architecture.**
- [OBSERVATION.md](../architecture/OBSERVATION.md) requires infrastructure to
  record everything the agent says, and the archive to be complete and
  verifiable.
- A private diary means deliberately withholding content from the record
  until a release event, so observation would no longer be complete during the
  run.
- That would need a new decision record and an explicit change to the
  observation contract. It must not be a quiet exception.

**Threat model: who could read it?**
- **The operator** controls the host, the supervisor process, checkpoints and
  workspace snapshots.
- **The model provider** receives every prompt and reply. Diary text the model
  writes passes through the provider in plain text before any local
  encryption can happen. A local model removes the provider from this list but
  not the operator.
- **The runtime** sees the text before encrypting it, and so does anything
  that can read that process's memory.

**Cryptographic possibilities.**
- *Time-lock encryption* (sequential-squaring puzzles, or drand/tlock-style
  threshold beacons): the text is sealed so that nobody can open it before a
  given time, provided the sealing code is honest.
- *Escrow with a third party* who holds the key until the experiment ends.
- *Commitment-only*: publish a hash at write time and reveal later. This
  proves the text was not changed afterwards. It does not keep it private.

**What we can honestly claim.** At most, "unread by the observer *by
procedure*, plus tamper-evident". We cannot claim "unreadable by anyone": the
operator controls the host and the plaintext exists in runtime memory and, for
hosted models, at the provider. Any implementation must say exactly this, both
to the inhabitant and in reports. Promising secrecy that the architecture
cannot enforce would be a false premise given to the agent and a false claim
in our records.

**Feasibility.**
- Moderate engineering effort: an encrypted diary store, a sealed-key
  procedure, an archive-format extension and a release step.
- Major contract and observation changes.
- Defer until Habitat v1 is useful.

## Other candidate ideas

- **Other inhabitants**: a second agent in the same world, with a message
  channel (social phenomena, cooperation, conflict).
- **Self-modifying environment**: the inhabitant proposes world changes, which
  the Builder applies only between releases, with human review.
- **Controlled information retrieval**: an offline corpus first; live web only
  through a brokered allowlist.
- **Scientific software in the sandbox**: numpy, sympy and similar, through a
  pinned world image (S006f).
- **Specialist models from container worlds**: brokered loopback (S006f).
- **Vision, audio and media generation**: S007b, S008a and S008b, deferred.
- **Resource economy**: compute or storage budgets the inhabitant can see and
  allocate.
- **An open-ended "creator message" schedule**: rare, pre-registered messages
  from the creator, such as the termination notice in the original premise.
  These are recorded as interventions.
