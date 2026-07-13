# Session Insights — Vicarious (re-run 2026-07-12, post-divergence)

> Re-run after a **parallel session built in the background**. This session's
> transcript covers the *conversation* thread (reset → pitch → handoff); the git
> history covers the *build* thread (a parallel agent that committed to the repo
> but did not log reasoning in this project dir). Insights below are grounded in
> **git history + files on disk** = verifiable truth, not remembered claims.

## Executive summary — top patterns

1. **Two threads ran in parallel and nearly desynced.** A conversation thread
   (this transcript) and a build thread (git commits `ade861a`→`09a0e93`) advanced
   the same project simultaneously. The conversation thread twice asked to commit
   work / handle files that the build thread had *already* committed. **Cost:**
   wasted a clarifying round on moot questions. **Fix:** re-verify git state at the
   top of every turn when parallel sessions are possible (done now).

2. **"Handoff" was requested repeatedly but kept dissolving into workflow.** User
   asked for Cowork handoff (session ~U5), pitch handoff (U10), and "what happened
   to the handoff" (this turn). The recurring miss: treating the follow-along
   *medium* (Cowork/Cursor/dashboard) as if it satisfied the *artifact* request.
   **Fix:** `COWORK_HANDOFF.md` now exists as a discrete, in-repo packet.

3. **The `/reset` discipline directly enabled the world-model pivot.** Stripping
   the over-scoped agent crew (`8d7d639`) left a clean swappable-backend seam
   (`frame_source.py`), which `world_model.py` then copied verbatim to add gamify
   (`b5373e4`) with zero core changes. **Lesson: aggressive decrufting paid off.**

4. **Demo-safety-first is a consistent, correct instinct.** Every risky capability
   ships with a no-dependency fallback: `FakeWorld` (no API), `dev/fal_world.mp4`
   (backup clip if live gen fails), webcam standing in for glasses. This is the
   single strongest pattern in the build and should be a stated project rule.

5. **Interactive-menu-at-every-fork worked, but menus were sometimes moot.** Menus
   were asked even when the answer was already determined by disk state (the commit
   question). **Fix:** verify state *before* composing the menu.

## Build arc (from git — the verifiable record)

```
8d7d639  Strip agent crew → fundamental product   (the /reset)
ade861a  MVP verified: uv + dashboard + frame-drop tolerance
b5373e4  World-model Tier-1: gamify POV → generated world
c7c42cb  Real world model: fal.ai LTX image→video backend
3a1eb3b  Demo polish: prompts, style presets, backup fallback
09a0e93  (+ artifact/gitignore housekeeping)
```
Went from 451 LOC (reset baseline) → ~579 LOC product, plus a real generative
world-model demo. All committed, working tree clean.

## Encapsulation candidates

### [Parallel-session drift guard] — warning + habit · confidence: high
**Evidence:** two turns spent on already-done work.
**Fix:** when parallel sessions are possible, run `git log --oneline -5` +
`git status` before proposing actions. Cheap, prevents moot menus.

### [Demo-safety as a project rule] — CLAUDE.md / project-doc addition · high
**Evidence:** `FakeWorld`, backup clip, webcam fallback all independently added.
**Draft rule:** "Every external-dependency feature ships with a no-dependency
fallback that keeps the demo flowing." Already implicit; make it explicit.

### [Handoff = artifact, not medium] — resolved · high
**Evidence:** three handoff asks, one persistent gap.
**Encapsulation:** `COWORK_HANDOFF.md` (in-repo cold-start packet) +
`PITCH_HANDOFF.md` (deck source). Pattern: a "handoff" request means *produce a
file*, not *work in the collaborative tool*.

## Suggested next actions

1. Commit `COWORK_HANDOFF.md` + this insights file (close the documentation loop).
2. Reconcile `PITCH.md` (parallel session) vs `../PITCH_HANDOFF.md` (this session)
   — likely overlapping; pick one as canonical for the deck.
3. Proceed to Mentra glasses (task #8) — the one real capability still stubbed.
