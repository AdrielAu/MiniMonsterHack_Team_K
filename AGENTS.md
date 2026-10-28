# AGENTS.md

Instructions for every coding agent in this repo (Claude Code, Codex, Antigravity, and others).

## Before you start

- **Any code change** (writing, editing, refactoring or reviewing code): read `docs/agents/coding-standards.md` first and follow it.
- **Any frontend, UI or visual design work**: read `docs/agents/frontend-workflow.md` first and follow its steps in order.
- **Any video, motion graphic, captions or overlay**: load the `hyperframes` skill and read it before doing anything else.
- **Any hackathon planning or build work**: read `docs/competition/README.md` first. Competition rules there override default assumptions.

## Competition

Team K's entry to the Mini Monster Hack (28 Oct 2026). Rules: `docs/competition/student-guide.md`. Our plan (accuracy through TEST 1, then speed to FINAL): `docs/competition/strategy.md`.

## Design truth

- `DESIGN.md` (visual system) and `PRODUCT.md` (audience, purpose, voice) at the repo root are the only design sources of truth.
- Never create another theme, palette, token or design-spec file (`design-system/`, `MASTER.md`, `theme.md`, `brand.md` and the like). If a skill wants to write one, put that content into `DESIGN.md` instead.
- In code, design tokens live in exactly one file, which `DESIGN.md` names.

## Skills

- Skills live once, in `.agents/skills/`, and are committed. `.claude/skills` is a local link to that folder. If it is missing, run `scripts/link-skills.ps1` (Windows) or `scripts/link-skills.sh`.
- Install new skills with `npx skills add <source> -a codex -y` so they land in `.agents/skills/` only.
- Update every skill with `scripts/update-skills.ps1` or `scripts/update-skills.sh`.
- Only use the `unslop` skill when the user explicitly asks for it.

## Project

A Monster Detector for Learning Analytics data (see `GLOSSARY.md`). No CI/CD or pytest: see the hackathon override in `docs/agents/coding-standards.md`.

**Stack:** Python 3.12 + DuckDB, managed with `uv` (`uv sync` once to install).

- **Data:** copy the organisers' folders into `data/` (gitignored, never commit it): `data/General Files/`, `data/Training/`, `data/Test/`, `data/Predict/`.
- **Loader:** `from detector.load import connect; con = connect("training")` (or `"test"`, `"predict"`) gives a DuckDB connection with every table as a view named without its prefix (`person_dim`, `lms_item_activity_by_session_fact`, ...) plus `activity`, a merged LMS + video timeline with `ts` (UTC) and `ts_local` (UK time).
- **Check the loader:** `uv run python -m detector.load training` prints row counts.
- Run detector scripts as modules from the repo root: `uv run python -m detector.<monster>`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues on AdrielAu/MiniMonsterHack_Team_K (via `gh`). See `docs/agents/issue-tracker.md`.

### Triage labels

Default labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
