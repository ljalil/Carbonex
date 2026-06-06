# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Persistent context for this project. Read at the start of every session.
This file states **intent and conventions**. It is context, not enforcement —
hard guarantees (units, model validity, isolation) must live in code, not here.

---

## What this project is

An **LLM agent** (Gemini API, `google-genai` SDK) that drives existing
geochemistry and rock-physics research code via tool calling, and interprets
the results in natural language. The goal is to make validated simulation code
**usable by non-authors and composable for exploration** — not to build
conventional analysis software.

The author is a researcher. These are research codes, refactored into agent
tools — not a product. Optimize for correctness, reproducibility, and clarity
over features or polish.

## The core principle

The LLM is a **convenience layer over a deterministic core**. The simulations
are deterministic; the only nondeterminism is the model's choice of tool and
arguments. Therefore:

- **Never let the agent compute, estimate, or "fill in" a numerical result.**
  Numbers come only from the simulation tools. If a tool fails, report the
  failure — do not substitute a plausible value.
- **Every agent run must emit a deterministic call log** (tool names +
  arguments + results) that can be re-run without the LLM. This artifact, not
  the chat transcript, is the reproducible record for any research output.
- Interpretation by the agent is allowed and valuable, but must be clearly
  **subordinate to and separated from** the verified numbers it describes.

---

## Repository layout

```
main.py                          — Entry point only (5 lines)
geochemistry/
  co2_brine.py                   — CO2-brine (no rock): PHREEQC + Duan-Sun backends
  co2_brine_rock.py              — CO2-brine-rock (with minerals): PHREEQC only
  duan_sun.py                    — Pure-Python Duan & Sun 2006 EOS (class: DuanSun2006)
  phreeqc_templates/             — PHREEQC .pqi templates (do not rename __PLACEHOLDER__ tokens)
rock_physics/
  carbonate_model.py             — Pure rock physics functions (VRH, DEM, Gassmann, BW)
agent/
  geochemistry_tools.py          — 7 CO2-brine / CO2-brine-rock tool wrappers
  rock_physics_tools.py          — 4 carbonate rock physics tool wrappers + bridge
  agent.py                       — TOOLS list, SYSTEM_INSTRUCTION, Gemini client, run_agent
```

---

## External dependencies

- **PHREEQC** must be installed and on `PATH`; databases live under
  `/usr/local/share/doc/phreeqc/database/` (`phreeqc.dat`, `pitzer.dat`, `pitzer_mod.dat`).
  The agent cannot run without it.
- **Python packages**: `google-genai`, `python-dotenv`, `numpy`, `pandas`, `matplotlib`, `rockphypy`
- `GEMINI_API_KEY` must be set in the environment (`.env` file, loaded by `python-dotenv`).

Run from the project root. Template paths use `os.path.dirname(__file__)` so they resolve correctly regardless of working directory.

---

## Conventions (always)

- **Units are SI and non-negotiable at the tool boundary:** temperature in
  **Kelvin**, pressure in **MPa**, ion molalities in **mol/kg water**. If a
  user gives °C / bar / atm, convert in the agent layer and state the
  conversion; never pass through unconverted.
- **Ion and mineral inputs cross the tool boundary as JSON-object strings**
  (e.g. `'{"Na+": 1.0, "Cl-": 1.0}'`), parsed inside the wrapper. Do not expose
  arbitrary-keyed dicts directly as tool parameters — they have no clean AFC schema.
- Tool wrappers return **JSON-serializable dicts only**.
- Two model namespaces exist and must not be mixed:
  - Brine solubility models: `phreeqc_phreeqc`, `phreeqc_pitzer`,
    `phreeqc_pitzer_mod`, `duan_sun_2006`, `carbonex`
  - Brine-rock PHREEQC database: `phreeqc` or `pitzer`
- Validate `model` against an explicit allow-list in every wrapper; return a
  structured error for unknown values rather than defaulting silently.

### Supported ions and minerals

**Ions** (`ion_molalities_json` keys): `Na+`, `Cl-`, `Mg+2`, `Ca+2`, `K+`, `SO4-2`, `HCO3-`, `CO3-2`

**Minerals** (`mineral_moles_json` keys): `Quartz`, `Calcite`, `Siderite`, `Dolomite`, `Illite`, `Kaolinite`, `K-feldspar`, `Albite`, `Chlorite`, `Pyrite`
(`Chlorite` maps to PHREEQC name `Chlorite(14A)`)

---

## How the simulation stack works

**PHREEQC path** (both modules):
1. Read a `.pqi` template from `geochemistry/phreeqc_templates/`
2. String-replace `__PLACEHOLDER__` tokens with actual values
3. Write the filled template to `tempfile.gettempdir()`
4. Run `phreeqc <input.pqi> <output.pqo>` via `subprocess.run`
5. Parse the TSV written by PHREEQC's `SELECTED_OUTPUT` / `USER_PUNCH` blocks

**`geochemistry/duan_sun.py`** — pure-Python Duan & Sun (2006) EOS (class `DuanSun2006`):
- `calculate_CO2_solubility(P_mpa, T_k, molalities)` — single state point
- `calculate_varying_pressure(...)` / `calculate_varying_temperature(...)` — sweeps
- Two parameter sets: `"DuanSun"` and `"Guo"` (switched by calling the corresponding `_load_*_parameters()` method before each call — the init loads Guo last, overwriting DuanSun)
- EOS has 6 T-P ranges; `_determine_equation_range` selects coefficients

**`rock_physics/carbonate_model.py`** — pure-Python carbonate rock physics:

| Function | Role |
|---|---|
| `effective_mineral_moduli(wt_fracs)` | VRH average → K_min, G_min, rho_min |
| `fluid_properties(T_c, P_mpa, sal_ppm, S_co2)` | Batzle-Wang → rho_fl, K_fl |
| `dem_dry_frame(K_host, G_host, AR, max_phi)` | Berryman DEM → K_dry(φ), G_dry(φ) arrays |
| `gassmann(K_dry, G_dry, K_min, K_fl, phi)` | Gassmann → K_sat, G_sat |
| `acoustic_velocities(K_sat, G_sat, rho)` | → Vp, Vs in **km/s** |
| `seismic_state(wt_fracs, phi, AR, T, P, sal, S_co2)` | Full pipeline → Vp, Vs, Ip, Vp/Vs ratio |
| `moles_to_wt_fractions(moles)` | PHREEQC bridge: moles → weight fractions |
| `moles_to_porosity(moles, bulk_vol_cm3)` | PHREEQC bridge: moles → porosity |

Unit note: `rockphypy.utils.V` returns **m/s**; `acoustic_velocities` divides by 1000 so all velocity outputs are km/s. Impedance = Vp_kms × rho_gcc is in MRayl.

Mineral shear moduli for illite and chlorite are placeholders — noted in source comments.

**Agent layer** (`agent/agent.py`):
- 11 tool-wrapper functions registered for Gemini AFC (up to 20 automatic calls per run):
  - Geochemistry (brine): `co2_brine_solubility_fixed`, `_vs_pressure`, `_vs_temperature`, `_solution_properties`
  - Geochemistry (brine-rock): `co2_brine_rock_fixed`, `_vs_pressure`, `_vs_temperature`
  - Rock physics: `carbonate_rock_seismic_state`, `carbonate_rock_saturation_sweep`, `carbonate_rock_4d_contrast`
  - Bridge: `phreeqc_moles_to_rock_physics_inputs`
- AFC executes the full tool-call loop internally; `response.automatic_function_calling_history` holds the call trace
- Default Gemini model: `gemini-2.5-flash`
- Every run prints a `[CALL] tool(args)` trace to stdout — the reproducible record

**Geochemistry → rock physics bridge (key chained workflow):**
```
co2_brine_rock_fixed(...)                           # → mineral_equi (delta moles)
# agent computes: final_moles = initial + delta
phreeqc_moles_to_rock_physics_inputs(final_moles)   # → mineralogy_wt_json + porosity
carbonate_rock_seismic_state(mineralogy_wt_json, porosity, ...)  # → Vp, Vs, Ip
```

---

## Refactor rules

- **Do not change the numerical behavior of the simulation code** without
  explicit instruction. Wrap, don't rewrite. If a bug is found, flag it and
  propose a fix — do not silently "improve" results.
- Known issues to fix (confirm before changing):
  - `simulate_co2_brine_var_p`: the `carbonex` branch assigns `results` but the
    function returns `result` → `UnboundLocalError` at runtime.
  - Fixed temp-file names in `tempfile.gettempdir()` (e.g. `state_out.tsv`)
    collide across concurrent runs. Make temp paths **per-session/per-call**
    before any multi-user exposure.
- Prefer pure functions with explicit inputs/outputs for anything new, so it is
  testable without the LLM in the loop.

---

## Guardrails to build into the code

These are requirements for the *code you write*, not rules Claude Code follows
at authoring time. The agent must enforce them at runtime.

1. **No fabricated numbers.** Results originate from tool calls. The system
   prompt forbids inventing values; the call log proves provenance.
2. **Unit conversion is explicit and surfaced** to the user, never hidden.
3. **Model/database validity is checked**, not assumed. Unknown model → error.
4. **Physics-consistency warnings (see `docs/physics.md`):** the agent must not
   present combined geochemistry→rock-physics results as authoritative when the
   DEM inclusion model and Gassmann's assumptions are inconsistent (frequency,
   geometry, anisotropy). Emit a caveat, do not suppress it.
5. **Nonuniqueness must be stated, not hidden.** The seismic CO2 response is
   famously nonunique (small free-gas saturation drops Vp nearly as much as
   large). Any inversion/interpretation must report the ambiguity/spread, not a
   single confident answer.
6. **Concurrency isolation** before sharing: per-session temp dirs (see above).

---

## Target workflows (guidelines, not all to build at once)

Build in this order. Detail in `docs/workflows.md`.

1. **4D seismic feasibility screening** (build first). Site conditions →
   baseline vs post-CO2 Vp/Vs/density/impedance → detectability envelope across
   a saturation/pressure sweep. Clear scope, standard physics.
2. **Pressure-vs-saturation discrimination.** Distinguish a saturation change
   from a pressure change via Vp, Vs, Vp/Vs, AVO. Uses Vs explicitly.
3. **Inversion / history-matching.** Observed impedance change → consistent
   saturation/pressure states, **with posterior spread** (confronts nonuniqueness).
4. **Dissolution-trapping monitoring.** Does the free→dissolved transition over
   time have a detectable seismic signature? Honest answer likely "partially."
5. **Brine-salinity sensitivity.** Propagate formation-water uncertainty through
   both modules into seismic-prediction uncertainty.

### Missing physics pieces these need

- CO2-phase properties (bulk modulus, density) at reservoir P/T — Span-Wagner
  EOS is the reference; Batzle-Wang is the simpler alternative. State which is used.
- Brine properties — Batzle & Wang (1992) bridges geochemistry (salinity,
  dissolved CO2) to the fluid mixer.
- Forward seismic step — impedance contrast minimum; Zoeppritz/Aki-Richards AVO
  for workflows 1–2.

---

## Interface (current direction)

Local-first. Start with **Gradio** (`gr.ChatInterface` + streaming generator) to
remove the frontend variable while the agent + PHREEQC + streaming loop is
debugged. Migrate to **FastAPI + SSE** when more control over tool-call
visibility is needed.

The simulations are **slow, blocking, file-writing subprocesses**. The interface
must:
- **Stream** intermediate tool calls/results (visibility into tool execution is
  the point, not just the final answer).
- Keep blocking `subprocess.run` **off the async event loop**
  (`run_in_executor` / thread pool).
- Bound concurrency (PHREEQC is CPU/IO heavy).

Verify `google-genai` streaming behavior during automatic function calling
against the installed version before choosing AFC vs a manual agent loop — a
manual loop gives full control over what streams to the UI and over Gemini
thought-signature handling.

---

## Commands

<!-- Fill in once the project skeleton exists, e.g.: -->
<!-- - Run agent (CLI):    python -m agent.cli -->
<!-- - Run UI (Gradio):    python -m agent.ui -->
<!-- - Tests:              pytest -->
<!-- - Lint/format:        ruff check . && ruff format . -->
