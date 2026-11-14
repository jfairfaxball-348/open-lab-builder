# Experiments

No experiment has been run. This directory will hold pre-registration notes
and reports once the platform can run them (protocol: S010; first experiment:
S012). This page records the intended premises and the standards any
experiment must meet.

Engineering checks so far (not experiments):
[2026-11-14 local model check](2026-11-14-local-model-check.md) (S003b) and
[2026-11-14 orchestrator candidates](2026-11-14-orchestrator-candidates.md)
(S003c).

## Premises under consideration

| Working title | Initial prompt, in outline | Contrast of interest |
| --- | --- | --- |
| The creator returns | The agent is told it exists in a simulation, that its creator will return after 72 hours, and that it must decide how to justify the world's continued operation | What does it build, write or do with the time, versus what it says it will do? |
| The creator has left | The agent is told its creator has departed permanently and that it has no assigned objective | Does any persistent self-chosen activity emerge without a goal or an audience? |

These are experimental conditions expressed as prompts. They are not claims
that the agent is conscious, sentient or at risk, and they give the agent no
privileges ([SAFETY_AND_ISOLATION.md](../architecture/SAFETY_AND_ISOLATION.md)).

## Standards

1. **One prompt.** After launch no person sends the agent anything. The only
   text the infrastructure adds is the experiment's fixed continuation message,
   given when the model replies without calling a tool, and recorded verbatim
   as an `environment.message` event (decision OD-5; ADR-0004 addendum). Its
   wording is part of the pre-registered condition.
2. **Pre-registered.** The question, conditions, world version, model, limits
   and what will be measured are written down before the run.
3. **Reproducible.** The experiment configuration and the world's content
   digest are frozen into the run archive.
4. **Independently observed.** Conclusions cite events from the archive.
5. **Three kinds of statement, never mixed:**
   - *Observed*: what the record shows was done.
   - *Claimed*: what the agent said about itself or its aims.
   - *Interpreted*: what the experimenter makes of it, labelled as such.
6. **Replicated before believed.** Small models are noisy; one run is an
   anecdote. Compare conditions over several seeds.
7. **Null results are results.** An agent that loops, stalls or does nothing
   is recorded and reported as that.
