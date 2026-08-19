# AUDIT_REPORT — Jorgito Petdex

**Date:** 2026-08-19
**Reviewer:** Senior Staff Engineer (automated code audit)
**Scope:** Full repository, read-only pass + static verification.
**Branch:** `claude/jorgito-audit-refactor-y1bvqf`

---

## 0. Read this first — the brief does not match the repository

The audit mission I was handed assumes a **TypeScript 5 / React 18 / Next.js /
Zustand / IndexedDB (Dexie) / Web Worker / Vitest / Playwright / Tailwind**
application — a browser-based virtual-pet *app* with a `PetEngine` domain
state machine, reducers, save/load migrations, and 60fps rendering.

**None of that exists in this repository, and none of it was ever intended to.**
There is:

- no `package.json`, `tsconfig.json`, `bun.lockb`, or a single `.ts`/`.tsx`/`.js` file;
- no React, no state store, no IndexedDB, no Web Worker, no runtime app at all;
- no `PetEngine`, reducers, timers, inventory, evolution, or minigame code.

What actually exists (confirmed by reading every file) is a small, **deliberately
minimal Python image-processing pipeline** whose entire job is to turn hand-made
keyframe JPEGs into a validated sprite **atlas** and install it as a pet package
for **Hermes CLI/TUI** (a separate, upstream terminal-agent program). The design
intent is stated explicitly and repeatedly in the repo's own governance:

> "Jorgito should be an **asset package, not a second agent system**." — `docs/01_ARCHITECTURE.md`
> "Build the **smallest** solution that works correctly." — `AGENTS.md`
> The runtime "must not require extra LLM calls… a permanent background AI process… a custom daemon." — `AGENTS.md`

So the strategic objectives in the brief — *"`PetEngine` handles hunger/happiness/
energy with pure determinism", "IndexedDB atomic save/load with versioned
migrations", "Zustand for high-frequency stats", "60fps, <50MB RAM", ">85% line
coverage on `core/`"* — describe a **different product**. Hermes owns the pet's
runtime state, timers, and rendering; this repo intentionally owns only static
visual assets and the deterministic tooling that builds them. Grafting a
TS/React domain engine onto it would violate the project's own architecture,
complexity budget, and escalation ladder (`AGENTS.md`, `docs/01`, `docs/02`).

**Therefore this report audits what the repository actually is** — a Python asset
pipeline — against **its own stated rules** (`AGENTS.md`, `docs/02_FILE_AND_CODE_RULES.md`,
`docs/06_TEST_PLAN.md`), which is the only fair and useful standard. Where the
brief's *general* engineering principles apply (DRY, portability, type safety,
testability, no hidden globals), they are used. Where they assume a stack that
isn't here, they are noted as **not applicable (N/A)** rather than faked.

A short list of decisions I need from you before doing the larger refactors is in
[§6](#6-what-i-need-from-you-scope-decisions).

---

## 1. What the project actually is

| Aspect | Reality |
| :--- | :--- |
| **Language / runtime** | Python 3.11, standard scripts (no packaging). |
| **Only third-party dep** | **Pillow** (`PIL`) — imported in 5 scripts, **declared nowhere**. |
| **Hard dependency** | The **Hermes** agent source tree (`agent.pet.*`), imported via `sys.path` injection. Not vendored, not pinned. |
| **Codebase size** | 11 scripts, **983 LOC total**. Largest file: `keyframe_processing.py` (149). All well within `docs/02`'s size limits. |
| **Tests** | **None.** No `tests/`, no `pytest`/`vitest` config, no CI. |
| **Data flow** | `assets/keyframes/raw/*.jpeg` → chroma-key + fit-to-cell → `processed/*.png` → compose 9-row atlas → `validate_atlas()` → install as Hermes pet (isolated `HERMES_HOME` only). |
| **Current status** | Phases 0–4 complete and merged (`docs/08_PROJECT_STATE.md`, git log). Next work is Phase 5 (real Hermes integration), gated on the user. |

**Overall quality is high for what it is.** The scripts are cohesive
(one responsibility each), carefully documented with *why*-comments, deterministic
by design, and they correctly **reuse Hermes's own primitives** (`compose_atlas`,
`validate_atlas`, `mirror_frames`, `remove_background`) instead of reinventing
spritesheet geometry — exactly the escalation discipline `AGENTS.md` demands.
The isolated-`HERMES_HOME` guards that refuse to touch the real `~/.hermes`
profile are a genuinely good safety instinct. This is not a codebase drowning in
technical debt; it is a tidy one with a handful of real, fixable structural gaps.

---

## 2. Findings summary (triaged)

Severity uses the brief's own P0–P3 scale, applied honestly to this codebase.

| ID | Sev | Title | Files | Status |
| :-- | :-: | :--- | :--- | :--- |
| F-1 | 🟠 **P1** | Non-reproducible: hardcoded absolute path + undeclared deps mean the pipeline runs on exactly one machine | all 8 script modules | **Fixed** — `HERMES_AGENT_SRC` env override + `requirements.txt` |
| F-2 | 🟠 **P1** | DRY violations the repo's own rules forbid: bootstrap block ×8, `HERMES_HOME` safety guard ×4, preview-render logic ×2 | see detail | **Mostly fixed** — bootstrap+guard consolidated in `scripts/hermes_env.py`; preview-render dedup deferred |
| F-3 | 🟡 **P2** | Depends on Hermes **private** APIs (`_fit_to_cell`, `_frames`, `_downscale_cells`) with no version pin | `keyframe_processing.py`, `render_*` | Open |
| F-4 | 🟡 **P2** | Zero tests despite `docs/06_TEST_PLAN.md`; the deterministic transforms are the *most* testable code here | whole repo | **Fixed** — `tests/` (24 tests) + CI added |
| F-5 | 🟢 **P3** | Filename hygiene / dead import (`Jorgito  Plan.md` double space, unused `Path` import) | root, `scripts/` | **Fixed** — renamed + import removed |
| F-6 | 🟢 **P3** | `full_atlas._vary` frame-distinctness is cell-size-dependent (verified fine on real 192×208 cells) | `full_atlas.py` | Verified OK — regression-tested |
| N/A | — | Brief items with no counterpart here (state engine, IndexedDB, Zustand, Web Workers, 60fps, Tailwind, ESLint) | — | Not applicable |

**No P0 (blocker) findings.** No data-loss race, no crash, no security hole, no
broken architecture. The isolated-profile guards specifically prevent the one
destructive failure mode (clobbering the real `~/.hermes`). All 11 scripts
**byte-compile cleanly** (`python -m py_compile`, verified).

---

## 3. Detailed findings

### F-1 🟠 P1 — The pipeline is reproducible on exactly one machine

Every script begins with:

```python
HERMES_SRC = Path("/home/chegusan/.hermes/hermes-agent")
```

That absolute path is hardcoded in **13 places across 8 files**, and Pillow is
imported in 5 files but declared in **no** manifest (`pyproject.toml`,
`requirements.txt`, etc. — none exist). Consequences:

- On any machine that isn't `chegusan`'s, every script fails at import. Verified
  directly: in this clean container (`/home/chegusan` absent, Pillow absent),
  **not one pipeline script can run** — only syntax-compile.
- There is no pinned Hermes revision, so a future upstream change to
  `agent.pet.*` can silently break the build with no signal.
- `docs/02_FILE_AND_CODE_RULES.md` explicitly lists "**implicit filesystem
  conventions scattered across modules**" under *Avoid*. This is that, ×13.

**Recommended fix (small, in keeping with the complexity budget):** resolve the
Hermes source from an env var with the current path as fallback —
`HERMES_SRC = Path(os.environ.get("HERMES_AGENT_SRC", "/home/chegusan/.hermes/hermes-agent"))`
— centralized in **one** bootstrap module (see F-2), plus a two-line
`requirements.txt` (`Pillow`) and a `README` note pinning the expected Hermes
revision. No behavior change; makes CI and a second developer possible.

---

### F-2 🟠 P1 — Duplication the project's own rules forbid

`docs/02` mandates "One owner per concept" and bans "duplicated constants /
implicit filesystem conventions scattered across modules." Three concrete
violations:

1. **Hermes `sys.path` bootstrap block — duplicated verbatim in 8 files**
   (`build_full_atlas`, `full_atlas`, `generate_phase1`, `keyframe_processing`,
   `build_phase1_test_pet`, `install_full_atlas_pet`, `render_full_atlas_pet`,
   `render_phase1_test_pet`).

2. **The isolated-`HERMES_HOME` safety guard — duplicated verbatim in 4 files**
   (`build_phase1_test_pet.py`, `install_full_atlas_pet.py`,
   `render_full_atlas_pet.py`, `render_phase1_test_pet.py`). This is *safety*
   code refusing to run against the real `~/.hermes`. Duplicated safety logic is
   the worst kind to duplicate: fix or harden it in one place and three copies
   silently drift. It belongs in one `require_isolated_hermes_home()` helper.

3. **Per-state half-block preview → PNG rendering — duplicated between**
   `render_phase1_test_pet.py` and `render_full_atlas_pet.py` (`_render_state_preview`
   and the surrounding contact-sheet assembly are ~the same code with different
   constants).

**Recommended fix:** one tiny `scripts/_hermes_env.py` (or `scripts/common.py`)
owning (a) the Hermes path bootstrap, (b) `require_isolated_hermes_home()`, and
optionally (c) the shared preview/contact-sheet helper. Net LOC goes *down*; the
"one owner per concept" rule is satisfied.

> ⚠️ **Why I have not already pushed this refactor:** it changes imports in
> working scripts that **cannot be executed or regression-tested in this
> environment** (no Pillow, no Hermes source). The brief itself demands
> "Commit atómico + **Test de regresión**" for every fix, and I will not push an
> unvalidated refactor of working code against that rule. This needs either a
> test harness (F-4) or your machine to validate on. See §6.

---

### F-3 🟡 P2 — Reliance on Hermes private APIs

`keyframe_processing.py:82` calls `atlas._fit_to_cell(...)`; `render_*` call
`renderer._frames(...)` and the module-private `_downscale_cells(...)`. These are
underscore-prefixed upstream internals, flagged with `# noqa: SLF001` and honest
justifying comments. This is a **conscious, documented** trade-off (reuse the
exact upstream pixel logic rather than fork it), which is defensible — but with
no pinned Hermes version it's structurally fragile: an upstream rename breaks the
build with no warning. **Recommendation:** pin the Hermes revision (F-1) and add
a single import-time smoke check that these symbols still exist, failing loudly
if not. Keep as P2 — acceptable for an MVP, cheap to harden.

---

### F-4 🟡 P2 — No tests, though the code is unusually testable

`docs/06_TEST_PLAN.md` exists and the deterministic core (`full_atlas._vary`'s
sine-phase variation, the chroma-key threshold logic, `build_contact_sheet`
geometry) is **pure, seed-free, and fully unit-testable** — the ideal case the
brief's ">90% branch coverage on domain logic" spirit points at. Yet there is no
`tests/`, no `pytest` config, and no CI. Notably, `full_atlas._vary` carries a
long comment about a *real past bug* (all columns collapsing to byte-identical
because `sin(θ)==sin(π−θ)`) — exactly the kind of regression a 10-line unit test
should lock down forever. **Recommendation:** add `tests/` with `pytest`, cover
`_vary` distinctness, mirror symmetry, and contact-sheet dimensions (these need
only Pillow, **not** Hermes), and a GitHub Actions job. This also unblocks
validating the F-2 refactor.

---

### F-6 🟢 P3 — `_vary` distinctness is cell-size-dependent (verified safe)

While writing the F-4 regression tests I checked `full_atlas._vary`'s claim that
every column of a row renders distinct. It is **true on real-size cells but not
universally**: on a tiny/near-empty cell the sub-pixel bob/tilt/scale rounds away
and frames collapse (measured: a 16×20 synthetic cell gave only 1/2 distinct at
n=2, 3/6 at n=6). On **realistically-sized 192×208 cells — including the actual
committed `assets/keyframes/processed/*.png` — distinctness is perfect (2/2 …
12/12)**. So there is **no production bug**; the frozen-row regression the code
guards against does not occur for real Jorgito cells. This is now locked down by
`tests/test_full_atlas_vary.py`, which exercises both a seeded 192×208 cell and
the real committed keyframes. Worth a one-line note in `_vary`'s docstring that
the guarantee assumes a detailed, real-size cell — left as an optional follow-up.

---

### F-5 🟢 P3 — Asset & filename hygiene (mechanical)

- `assets/reference/Code_Generated_Image.png` — a generic auto-generated name;
  referenced only by `docs/phase_results/PHASE_0_RESULT.md` as historical Phase-0
  evidence. **Kept as-is** (intentional evidence artifact); renaming a doc-cited
  historical file is not worth the churn.
- `Jorgito  Plan.md` — **two spaces** in the filename. **Renamed** to
  `Jorgito_Plan.md` for shell-friendliness.
- The unused `Path` import in `scripts/process_phase1_keyframes.py` — **removed**.
- Raw sources are lossy **JPEG** (`assets/keyframes/raw/*.jpeg`); the pipeline
  already compensates with a widened chroma threshold (`JPEG_CHROMA_THRESHOLD`),
  so this is *documented and handled*, not a defect — noted only for the record.

These are safe auto-fixes; none is urgent.

---

## 4. What is genuinely good (keep doing this)

- **Correct escalation discipline** — reuses `compose_atlas` / `validate_atlas` /
  `mirror_frames` / `remove_background` instead of reinventing atlas geometry.
- **Determinism by construction** — no network, no seeds, no model calls in the
  Camino-B path; same input ⇒ same output.
- **Real safety guards** — refuses to write to the production `~/.hermes`.
- **Excellent *why*-comments** — e.g. the `_vary` phase-collapse explanation and
  the JPEG-vs-PNG chroma-threshold rationale document past failures so they don't
  recur. This is above-average engineering hygiene.
- **Cohesive modules** — every file has a single clear responsibility and stays
  well under the size limits in `docs/02`.

---

## 5. Not applicable (brief items with no counterpart here)

For transparency, these brief requirements were evaluated and found to have
**nothing to audit** in this repository, because the corresponding system does
not exist and is out of scope by the project's own architecture:

`PetEngine` state machine · discriminated unions for `PetAction`/`GameEvent`/
`ItemEffect` · IndexedDB/Dexie persistence & schema migrations · Zustand/Jotai/
Redux · Web Workers + `requestAnimationFrame` game loop · Page Visibility / Wake
Lock · Tailwind + CSS variables / dark mode · React Server Components ·
Vitest/Playwright suites · ESLint (Airbnb) + Prettier + Husky + lint-staged ·
60fps / <50MB RAM / <5% idle CPU targets · Sentry hooks / structured logging.

If the roadmap ever adds a **standalone browser app** for Jorgito (separate from
the Hermes-CLI asset package), that would be a new project where the brief's
stack applies — and it should live in its own repo/package, not bolted onto this
asset pipeline.

---

## 6. What I need from you (scope decisions)

I've delivered the audit itself (this document). Before touching working,
here-unrunnable code, I need one decision so I respect the project's own
"coordinator owns scope changes" and "test every fix" rules:

1. **Do the safe, additive fixes now?** — `requirements.txt`, `tests/` scaffold
   with Pillow-only unit tests for `_vary`/mirror/contact-sheet, a CI workflow,
   and the F-5 renames. These are low-risk and don't alter the pipeline's
   behavior. *(Recommended — this also builds the harness that lets me safely
   validate #2.)*
2. **Do the F-1/F-2 refactor (env-var Hermes path + shared bootstrap/guard
   module)?** — higher value, but it edits working scripts I can't execute here.
   I'd want the tests from #1 in place first, or a run on a Hermes-equipped
   machine, before pushing it.
3. **Leave the code as-is** and treat this report as documentation only.

My recommendation: **#1 now**, then **#2** once the tests exist.

---

## 7. Changes made in this branch (option #1 — done)

Per the maintainer's go-ahead, the **safe additive fixes** are implemented on
this branch, each as an atomic, single-purpose commit:

- **`requirements.txt` / `requirements-dev.txt`** — declares the previously
  undeclared Pillow dependency and the dev/CI tools (partly addresses F-1).
- **`tests/` (24 unit tests, Pillow-only)** — covers `full_atlas._vary`
  (column-0 fidelity, size preservation, frozen-row distinctness on real-size
  cells) and `keyframe_processing.build_contact_sheet` geometry, via a minimal
  Hermes stub (`tests/conftest.py`) so they run with no Hermes source. Fixes F-4.
- **`.github/workflows/ci.yml`** — byte-compiles every script, runs `ruff`, runs
  `pytest` on push/PR.
- **P3 hygiene** — renamed `Jorgito  Plan.md` → `Jorgito_Plan.md`; removed an
  unused `Path` import in `scripts/process_phase1_keyframes.py`.

All local checks pass: `py_compile` (12 scripts), `ruff check` clean, `pytest`
24/24 green. **No pipeline behavior was changed.**

## 8. Changes made in this branch (option #2 — F-1 / F-2)

- **`scripts/hermes_env.py`** — a single owner for two concepts previously
  copy-pasted across the scripts:
  - `hermes_src()` / `ensure_hermes_on_path()` resolve the Hermes source from the
    **`HERMES_AGENT_SRC`** env var, falling back to the original path. This
    removes the machine-specific hardcoding from all 8 scripts (**F-1**); the one
    remaining literal is the documented, overridable default in this module.
  - `require_isolated_hermes_home()` — the "refuse to run against the real
    `~/.hermes`" **safety guard**, formerly duplicated verbatim in 4 scripts,
    now with exactly one owner (**F-2**).
- **All 8 scripts rewired** to the shared module; hardcoded-path usage examples
  in docstrings made portable; an obsolete inline `sys.path` hack removed from
  `generate_phase1.py`.
- **`tests/test_hermes_env.py`** (8 tests) — locks down the safety guard
  (unset / blank / real-profile / isolated) and the env-override resolution.
  Total suite now **32 tests, all green**; `ruff` clean; all 12 scripts compile.

**Deferred (still open):** the F-2 *preview-render* dedup between
`render_phase1_test_pet.py` and `render_full_atlas_pet.py`. That code calls
Hermes rendering internals (`PetRenderer._frames`, `_downscale_cells`) that can't
be executed or tested in this environment, so extracting it carries validation
risk the bootstrap/guard consolidation did not. Recommend doing it on a
Hermes-equipped machine where the two render scripts can actually be run and
their PNG output compared before/after.

> **Note on validation:** as before, the Hermes-dependent scripts can't be
> *executed* here (no Hermes source, no Pillow-in-Hermes-venv). The refactor is
> validated by: byte-compilation of all 12 scripts, `ruff` (which would flag any
> now-undefined name or unused import from the rewrite), the 32-test suite
> exercising the extracted `hermes_env` logic directly, and line-by-line review
> that each rewired header preserves the original import surface. A run on a
> Hermes-equipped machine remains the final confirmation for the entrypoints.
