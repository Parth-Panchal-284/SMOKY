# SMOKY — RocketRide side

Two pipelines plus the harness that runs them. Parallel specialist diagnosis,
then reconcile → repair → verify with a real rollback.

## 0. Setup (once)

```bash
pnpm init                                        # already done
pnpm add ./.rocketride/client/rocketride.tgz     # already done — vendored client, never the npm registry
```

`.env` is maintained by the RocketRide VS Code extension and is gitignored.
It already carries the connection pair. **You must add one LLM key** — staging
has no org-level LLM credential for this workspace:

```bash
echo 'ROCKETRIDE_ANTHROPIC_KEY=sk-ant-...' >> .env
```

## 1. Run it

```bash
# no LLM needed — deterministic stub findings, proves repair/verify/rollback
node --env-file=.env run.mjs --mode both --dry-run

# the real thing
node --env-file=.env run.mjs --mode parallel
node --env-file=.env run.mjs --mode sequential
node --env-file=.env run.mjs --mode both          # prints the timing comparison
```

Options: `--csv <path>` (default `data/sample.csv`), `--run-id <id>`, `--dry-run`.

Outputs: `out/cleaned.csv`, `out/evidence_report.json`, `data/telemetry.jsonl`.

## 2. Regenerate / validate the pipelines

```bash
node src/emit.mjs                       # regenerate every .pipe from the shared defs
node --env-file=.env src/validate.mjs   # validate all of them against staging
```

## Repo structure

| Path | What it is |
|---|---|
| `pipelines/diagnosis.pipe` | **Pipeline 1, parallel** — `chat` → 3 × `agent_rocketride` (one wave) → one `response_answers` |
| `pipelines/diagnosis_seq_*.pipe` | **Pipeline 1, sequential** — one single-specialist pipe each, run back-to-back |
| `pipelines/reconcile_repair.pipe` | **Pipeline 2** — chief agent that reconciles and classifies |
| `src/specialists.mjs` | The three specialist definitions — **shared by both modes** |
| `src/genpipe.mjs` | Generates the diagnosis pipes from those definitions |
| `src/genchief.mjs` | Generates the chief pipe; holds the binding conflict rules |
| `src/hotdata.mjs` | Hotdata interface: `MockHotdata`, `RealHotdata` (TODOs), `makeHotdata` swap |
| `src/profile.mjs` | Deterministic profiler + health score (used for BOTH before and after) |
| `src/repair.mjs` | Allow-listed transforms + audit trail |
| `src/verify.mjs` | Invariant checks + real rollback |
| `src/slice.mjs` | Per-specialist isolated data slice |
| `config/smoky.config.json` | Every tunable: LLM, thresholds, business ranges, allow-list, Hotdata flag |
| `run.mjs` | The harness — both modes, timing, telemetry, repair, verify |

## One model per agent

Each specialist runs on a **different** model, chosen for its job. This is the
whole point of a heterogeneous multi-agent system: the agents are not three
copies of one model with different prompts.

| Agent | Model | Tok/s | Why |
|---|---|---|---|
| `SCHEMA_MD` | `Qwen/Qwen3-30B-A3B-Instruct-2507` | 70 | Non-thinking Instruct variant. Null/type/format checks are mechanical. |
| `DUPLICATE_MD` | `deepseek-ai/DeepSeek-V4-Flash-0731` | 351 | 1M context — fuzzy grouping needs every row in view at once. |
| `ANOMALY_MD` | `deepseek-ai/DeepSeek-V4-Flash-0731` | 351 | Same model; proven to emit clean JSON under `agent_rocketride`. |
| `CHIEF` | `nvidia/Nemotron-3-Ultra-550b-a55b` | 523 | Tuned for multi-agent reasoning. Runs once per run, so cost is bounded. Note: **regional endpoint** (`us-central1`). |

### Model choice is constrained — read before swapping one

`agent_rocketride` requires **strict JSON** from its LLM. The engine retries 4
times and then fails the whole specialist:

```
LLM error: Failed to get valid JSON response after 4 attempts.
Last response: Here's a thinking process: 1. **Analyze User Input:** ...
        at (/opt/rocketride/ai/common/chat.py:595)
```

**Reasoning / "thinking" models narrate before answering and are rejected.**
Measured failures under `agent_rocketride`: `nvidia/Nemotron-3_5-Lightning` and
`zai-org/GLM-5.3-Flash` — both fast, both unusable here. This is NOT fixable
from the client: the rejection happens server-side before any response reaches
`extractJSON()`, and dropping `expectJson` on the `Question` does not change it.

Rule of thumb: pick the **Instruct** variant, never the **Thinking** one
(`Qwen3-30B-A3B-Instruct-2507` works; `Qwen3-30B-A3B-Thinking-2507` would not).

Configured in `config/smoky.config.json` under `llm.agents` — model, optional
per-agent `baseUrl`, and token budget. The generator emits one `llm_nebius`
node per agent using the `custom` profile, which accepts any Token Factory
routing key.

**Why this mattered:** the first working model was `Llama-3.3-70B-Instruct` at
**25 Tok/s** — the slowest option on the platform. One specialist took 141s and
the three-agent wave blew past a 300s timeout. The current models are 70-523
Tok/s.

**Thread count is explicit.** `client.use()` takes `threads`; with it omitted
the server chooses, and the "parallel" wave can end up serialised — which would
make the whole comparison meaningless. Parallel mode requests one thread per
specialist; sequential mode explicitly requests 1, so the baseline is a real
baseline rather than an accident.

## Design decisions worth knowing

**Question.addContext() does not reach the model.** Measured: with the rows
passed via `addContext()` every specialist returned `{"findings": []}`; with
the identical rows inlined into the question text the same model returns
correct findings. `renderTable()` in `run.mjs` does the inlining — do not
"clean this up" back into `addContext`.

**Specialist logic is never duplicated.** `src/specialists.mjs` is the single
source of truth. `src/genpipe.mjs` emits the parallel pipe and the sequential
pipes from the same array — only the wiring differs.

**Sequential mode is three pipes, not one chained pipe.** RocketRide agents
consume the `questions` lane and produce `answers`, and the catalog has no
`answers → questions` converter, so agents cannot be chained inside one
pipeline. The harness runs the same generated single-specialist pipes back to
back — a faithful serial baseline with identical logic.

**Repair and verification are deterministic host-side code, not agent work.**
The spec allows "the SDK-code equivalent". An allow-listed transform set and a
real rollback cannot be delegated to a model and stay auditable. Only the chief
agent's *conflict reasoning* is LLM work, and its output is forced through a
closed enum host-side (`sanitizeDecisions`) whatever the model returns. If the
chief is unavailable, a deterministic fallback classifier takes over.

**Hotdata has two integration points, and they are different** (see the long
comment at the top of `src/hotdata.mjs`):
- *In-pipeline* create → query → destroy is native to the `db_hotdata`
  component. Set `hotdata.enabled = true` and supply `ROCKETRIDE_HOTDATA_*`;
  the generator then wires one isolated ephemeral DB per specialist. This
  variant is already validated against staging.
- *Host-side telemetry* (the persistent cross-session DB the dashboard queries
  live) is `log_event`, and it must be implemented from this process —
  pipelines run on RocketRide's servers and cannot reach a localhost endpoint.

**Idempotency.** Telemetry is deduplicated on `(run_id, agent, outcome, mode)`,
so re-running the same `run_id` cannot corrupt cross-session comparisons.

**Failure isolation.** In sequential mode a specialist that throws is logged
with `outcome: "failed"` and the run continues; the evidence report records the
gap. (In parallel mode the wave returns whatever answered.)

## Still open

- `ROCKETRIDE_ANTHROPIC_KEY` must be added to `.env` before a non-dry run.
- Hotdata credentials + `RealHotdata` implementation — teammate's half.
- The live telemetry dashboard (demo requirement) reads `data/telemetry.jsonl`
  today; point it at the persistent Hotdata DB once that exists.
- This folder is not a git repo yet; the submission checklist wants a repo link.
