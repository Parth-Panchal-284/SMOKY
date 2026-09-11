#!/usr/bin/env node
/**
 * Data ER harness — runs both pipelines end to end and prints the numbers the
 * demo needs: {mode, duration_ms} for the parallel-vs-sequential comparison,
 * before/after health score, and the full audit trail.
 *
 *   node --env-file=.env run.mjs --mode parallel --csv data/sample.csv
 *   node --env-file=.env run.mjs --mode sequential
 *   node --env-file=.env run.mjs --mode both
 *   node --env-file=.env run.mjs --mode both --dry-run    (no LLM; stub findings)
 */
import { readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import { RocketRideClient, Question } from 'rocketride';

import { parseCSV, toCSV } from './src/csv.mjs';
import { profileAndScore, numericBounds } from './src/profile.mjs';
import { SPECIALISTS, byId } from './src/specialists.mjs';
import { buildParallel, buildSequential } from './src/genpipe.mjs';
import { buildChief, ACTIONS } from './src/genchief.mjs';
import { buildSlice } from './src/slice.mjs';
import { extractJSON, answersOf, answerText } from './src/parse.mjs';
import { applyRepairs } from './src/repair.mjs';
import { verify } from './src/verify.mjs';
import { makeHotdata, telemetryEvent } from './src/hotdata.mjs';
import { publishTelemetry } from './src/publish_telemetry.mjs';

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : d; };
const flag = (k) => argv.includes(`--${k}`);

const cfg = JSON.parse(readFileSync('config/dataer.config.json', 'utf8'));
const csvPath = arg('csv', 'data/sample.csv');
const modeArg = arg('mode', 'parallel');   // fastest path; --mode both for the speedup comparison
const runId = arg('run-id', `run_${new Date().toISOString().slice(0, 19).replace(/[:T-]/g, '')}`);
const dryRun = flag('dry-run');

const hot = makeHotdata(cfg);
// Unbuffered progress log: node block-buffers stdout when it is not a TTY, so a
// long run shows nothing until it exits. appendFileSync flushes immediately.
const LOGFILE = dryRun ? 'out/run.dryrun.log' : 'out/run.log';
// Truncate at start: the log is a LIVE view of THIS run. Appending across runs
// made the console show a previous run's output above the current one, which
// reads as a broken UI.
try { mkdirSync('out', { recursive: true }); writeFileSync(LOGFILE, ''); } catch { /* non-fatal */ }
/** Bound any agent call so one slow wave cannot hang the demo. Rejects rather
 *  than resolving, so the caller's failure-isolation path handles it. */
function withTimeout(promise, ms, label) {
	let t;
	return Promise.race([
		promise.finally(() => clearTimeout(t)),
		new Promise((_, rej) => { t = setTimeout(() => rej(new Error(`${label} timed out after ${ms}ms`)), ms); }),
	]);
}

const log = (...a) => {
	const line = a.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join(' ');
	console.log(line);
	try { mkdirSync('out', { recursive: true }); appendFileSync(LOGFILE, `[${new Date().toISOString().slice(11, 19)}] ${line}\n`); } catch {}
};
const ms = (t) => Math.round(t);

/** ---------------------------------------------------------------- intake */
function intake() {
	const { header, rows } = parseCSV(readFileSync(csvPath, 'utf8'));
	const { profile, score } = profileAndScore(header, rows);
	return { header, rows, profile, score };
}
/** The spec's stub: a separate intake step already validated + profiled. */
export function get_profiled_dataset(_run_id) { return intake(); }

/** ------------------------------------------------------- diagnosis (P1) */

/**
 * Render the rows INLINE in the question text.
 *
 * Question.addContext() does not reach the model through this pipeline —
 * measured: with addContext every specialist returned {"findings": []}; with
 * the identical data inlined here the same model returns correct findings.
 * Keep the data in the prompt body.
 */
function renderTable(ds) {
	return ds.rows
		.map((r, i) => `${i}: ${ds.header.map((h) => `${h}=${JSON.stringify(r[h] ?? '')}`).join(', ')}`)
		.join('\n');
}
/**
 * The SAME envelope for both modes — if the payloads differed, the
 * parallel-vs-sequential wall-clock comparison would be meaningless.
 * `spec` is optional: in parallel mode all three agents share one envelope.
 *
 * Note on isolation: in context-mode every specialist sees the same rows and
 * isolation is enforced by its instructions. TRUE per-specialist data
 * isolation is the hotdata.enabled path, where each agent gets its own
 * ephemeral db_hotdata database loaded with only its slice (src/slice.mjs).
 */
function diagnosisQuestion(ds, spec = null) {
	// NOT expectJson: the engine enforces strict JSON server-side and retries 4x
	// before erroring. Reasoning models (Nemotron-Lightning, GLM-5.3-Flash)
	// narrate before answering, so every one of those attempts is rejected and
	// the whole specialist fails. Take the prose and extract client-side
	// instead — extractJSON() strips reasoning and finds the payload.
	const q = new Question();
	const forAll = spec == null;   // parallel wave: one envelope, all three read it
	q.addQuestion([
		spec ? `Diagnose this dataset as ${spec.id}.` : 'Diagnose this dataset for your own specialty only.',
		'',
		`Dataset (${ds.rows.length} rows, columns: ${ds.header.join(', ')}).`,
		'The number before each colon is the 0-based __row index to use in affected_rows:',
		renderTable(ds),
		'',
		// Quartiles are arithmetic — hand them over precomputed rather than making
		// the specialist derive them (it exhausts its waves and returns nothing).
		...(spec?.id === 'ANOMALY_MD' || forAll
			? [
					'Precomputed IQR bounds per numeric column (k=' + cfg.anomaly.iqrMultiplier + '):',
					JSON.stringify(numericBounds(ds.header, ds.rows, cfg.anomaly.iqrMultiplier), null, 0),
					'A value outside [lower_fence, upper_fence] is a statistical_outlier.',
					`Business ranges: ${JSON.stringify(cfg.anomaly.businessRanges)} — a value outside these is a business_range_violation even if inside the fences.`,
					'Do NOT recompute the quartiles. Use the numbers above and report which rows violate them.',
					'',
				]
			: []),
		'Now return your findings JSON.',
	].join('\n'));
	return q;
}

async function runAgentsParallel(client, ds) {
	const pipeline = buildParallel(cfg);
	const t0 = performance.now();
	// One execution thread per specialist — without this the server picks the
	// thread count and the three agents can end up serialised inside the wave,
	// which would make the parallel-vs-sequential comparison meaningless.
	const { token } = await client.use({
		pipeline, ttl: cfg.run.ttlSeconds,
		threads: cfg.run.threadsParallel ?? Math.max(4, SPECIALISTS.length),
		name: `dataer-diagnosis-parallel-${runId}`,
	});
	try {
		// One wave: every specialist receives the same envelope and answers together.
		const res = await withTimeout(
			client.chat({ token, question: diagnosisQuestion(ds) }),
			cfg.run.agentTimeoutMs, 'parallel wave');
		const duration = performance.now() - t0;
		const answers = answersOf(res);
		log(`  fan-out returned ${answers.length} answer(s) (expected ${SPECIALISTS.length})`);
		return { answers, duration, raw: res };
	} finally { await client.terminate(token).catch(() => {}); }
}

async function runAgentsSequential(client, ds) {
	const built = buildSequential(cfg);
	const answers = [];
	const perAgent = [];
	const t0 = performance.now();
	for (const { spec, pipeline } of built) {
		const a0 = performance.now();
		let outcome = 'ok', text = null;
		try {
			const { token } = await client.use({
				pipeline, ttl: cfg.run.ttlSeconds, threads: 1,
				name: `dataer-diagnosis-seq-${spec.id}-${runId}`,
			});
			try {
				const res = await withTimeout(
					client.chat({ token, question: diagnosisQuestion(ds, spec) }),
					cfg.run.agentTimeoutMs, spec.id);
				text = answersOf(res)[0] ?? null;
			} finally { await client.terminate(token).catch(() => {}); }
		} catch (e) {
			outcome = 'failed'; text = null;
			log(`  ! ${spec.id} failed: ${String(e.message).slice(0, 120)}`);
		}
		const dur = performance.now() - a0;
		perAgent.push({ agent: spec.id, duration_ms: ms(dur), outcome });
		await hot.log_event('telemetry', telemetryEvent({ run_id: runId, agent: spec.id, mode: 'sequential', query_count: 1, duration_ms: ms(dur), outcome }));
		if (text) answers.push(text);
	}
	return { answers, duration: performance.now() - t0, perAgent };
}

function stubAnswers(ds) {
	// --dry-run: deterministic findings so the repair/verify path can be tested
	// without an LLM. Mirrors what the specialists should return.
	const dateCol = ds.header.find((h) => ds.profile.columns[h].mixedDateFormats);
	const nullCols = ds.header.filter((h) => ds.profile.columns[h].nullCount > 0);
	const dupRows = ds.profile.duplicateGroups.flatMap((g) => g.rows);
	const out = [
		{ agent: 'SCHEMA_MD', findings: [
			...(dateCol ? [{ finding_type: 'inconsistent_date_format', severity: 'medium', affected_columns: [dateCol],
				affected_rows: ds.rows.map((_, i) => i), evidence: `${dateCol} mixes ${ds.profile.columns[dateCol].dateShapes.join(' and ')}`,
				proposed_action: 'standardize_date_format' }] : []),
			...(nullCols.length ? [{ finding_type: 'null_values', severity: 'medium', affected_columns: nullCols,
				affected_rows: ds.rows.map((_, i) => i), evidence: `nulls in ${nullCols.join(', ')}`,
				proposed_action: 'fill_null_with' }] : []),
		] },
		{ agent: 'DUPLICATE_MD', findings: dupRows.length ? [{ finding_type: 'exact_duplicate', severity: 'high',
			affected_columns: [], affected_rows: dupRows, evidence: `rows ${dupRows.join(', ')} normalise identically`,
			proposed_action: 'merge_duplicate_rows' }] : [] },
		{ agent: 'ANOMALY_MD', findings: [{ finding_type: 'business_range_violation', severity: 'high',
			affected_columns: ['age'], affected_rows: ds.rows.map((r, i) => (Number(r.age) > 120 ? i : -1)).filter((i) => i >= 0),
			evidence: 'age above configured maximum 120', proposed_action: 'flag_outlier' }] },
	];
	return out.map((o) => JSON.stringify(o));
}

function mergeFindings(answers, label = '') {
	const findings = [];
	const gaps = [];
	// Always dump raw replies — when a model returns something unexpected this
	// file is the only way to see what it actually said.
	try {
		writeFileSync(`out/raw_${label || 'answers'}.json`, JSON.stringify(answers, null, 2));
	} catch { /* non-fatal */ }
	for (const a of answers) {
		const parsed = extractJSON(a);
		if (!parsed || !Array.isArray(parsed.findings)) { gaps.push(answerText(a).slice(0, 400)); continue; }
		const agent = parsed.agent ?? 'UNKNOWN';
		for (const f of parsed.findings) findings.push({ ...f, agent });
	}
	return { findings, gaps };
}

/** ----------------------------------------------- reconcile & repair (P2) */
async function runChief(client, findings) {
	if (!findings.length) return { decisions: [], duration: 0 };
	const pipeline = buildChief(cfg);
	const t0 = performance.now();
	const { token } = await client.use({ pipeline, ttl: cfg.run.ttlSeconds, name: `dataer-chief-${runId}` });
	try {
		const q = new Question();
		q.addQuestion([
			'Reconcile these specialist findings and return your decisions JSON.',
			'',
			`Allowed transforms: ${cfg.repair.allowedTransforms.join(', ')}.`,
			'',
			'Findings:',
			findings.map((f, i) => `${i}: ${JSON.stringify({ agent: f.agent, ...f })}`).join('\n'),
		].join('\n'));
		const res = await withTimeout(
			client.chat({ token, question: q }), cfg.run.agentTimeoutMs, 'chief');
		const parsed = extractJSON(answersOf(res)[0]);
		return { decisions: parsed?.decisions ?? [], duration: performance.now() - t0, rawText: answersOf(res)[0] };
	} finally { await client.terminate(token).catch(() => {}); }
}

/** Deterministic fallback when the chief is unavailable or returns nothing. */
function fallbackDecisions(findings) {
	return findings.map((f, i) => {
		const t = f.proposed_action;
		const allowed = cfg.repair.allowedTransforms.includes(t);
		const isAnomaly = f.agent === 'ANOMALY_MD';
		return {
			finding_index: i, agent: f.agent,
			action: !allowed ? 'ignore' : isAnomaly && t !== 'flag_outlier' ? 'flag_for_review' : 'auto_fix',
			transform: allowed ? t : 'none',
			reasoning: 'deterministic fallback: chief agent unavailable; allow-list + rule 3 applied',
		};
	});
}

/** Enforce the closed enum host-side, whatever the model returned. */
function sanitizeDecisions(decisions, findings) {
	return decisions
		.filter((d) => Number.isInteger(d.finding_index) && d.finding_index >= 0 && d.finding_index < findings.length)
		.map((d) => ({
			...d,
			action: ACTIONS.includes(d.action) ? d.action : 'flag_for_review',
			transform: cfg.repair.allowedTransforms.includes(d.transform) ? d.transform : 'none',
		}));
}

/** ------------------------------------------------------------------ main */
async function diagnose(client, ds, mode) {
	log(`\n=== DIAGNOSIS (${mode}) ===`);
	if (dryRun) {
		const t0 = performance.now();
		const answers = stubAnswers(ds);
		const duration = performance.now() - t0;
		for (const s of SPECIALISTS)
			await hot.log_event('telemetry', telemetryEvent({ run_id: runId, agent: s.id, mode, query_count: 0, duration_ms: ms(duration / 3), outcome: 'ok', note: 'dry-run' }));
		return { answers, duration };
	}
	if (mode === 'parallel') {
		const r = await runAgentsParallel(client, ds);
		for (const s of SPECIALISTS)
			await hot.log_event('telemetry', telemetryEvent({ run_id: runId, agent: s.id, mode, query_count: 1, duration_ms: ms(r.duration), outcome: r.answers.length ? 'ok' : 'failed' }));
		return r;
	}
	return runAgentsSequential(client, ds);
}

async function main() {
	mkdirSync('out', { recursive: true });
	const ds = get_profiled_dataset(runId);
	log(`run_id=${runId}  csv=${csvPath}  rows=${ds.rows.length}  cols=${ds.header.length}`);
	log(`baseline health score: ${ds.score}`);
	await hot.ensure_telemetry_db();

	let client = null;
	if (!dryRun) {
		// persist: automatic reconnection. Long agent waves (especially with the
		// Hotdata tool, which needs more turns) outlive a single websocket;
		// without this a dropped socket kills the whole run mid-wave.
		client = new RocketRideClient({
			uri: process.env.ROCKETRIDE_URI,
			auth: process.env.ROCKETRIDE_APIKEY,
			persist: true,
			onConnectError: (e) => log(`  ~ reconnecting: ${String(e?.message ?? e).slice(0, 80)}`),
		});
		await client.connect();
	}

	const modes = modeArg === 'both' ? ['parallel', 'sequential'] : [modeArg];
	const timings = [];
	let chosen = null;

	try {
		for (const mode of modes) {
			let r;
			try {
				r = await diagnose(client, ds, mode);
			} catch (e) {
				log(`  ! ${mode} mode failed: ${String(e.message).slice(0, 160)}`);
				timings.push({ mode, duration_ms: null, outcome: 'failed' });
				await hot.log_event('telemetry', telemetryEvent({
					run_id: runId, agent: 'WAVE', mode, duration_ms: 0, outcome: 'failed',
					note: String(e.message).slice(0, 200),
				}));
				continue;
			}
			timings.push({ mode, duration_ms: ms(r.duration) });
			const merged = mergeFindings(r.answers, mode);
			log(`  findings: ${merged.findings.length}${merged.gaps.length ? `  (unparseable replies: ${merged.gaps.length})` : ''}`);
			for (const g of merged.gaps) log(`    ? unparsed: ${g.replace(/\s+/g, ' ').slice(0, 220)}`);
			for (const f of merged.findings) log(`    [${f.agent}] ${f.finding_type} (${f.severity}) -> ${f.proposed_action}`);
			if (!chosen || merged.findings.length > chosen.findings.length) chosen = { ...merged, mode };
		}

		log('\n=== TIMING (parallel vs sequential) ===');
		for (const t of timings) log(`  ${JSON.stringify(t)}`);
		if (timings.length === 2) {
			const p = timings.find((t) => t.mode === 'parallel')?.duration_ms;
			const s = timings.find((t) => t.mode === 'sequential')?.duration_ms;
			if (p && s) log(`  speedup: ${(s / p).toFixed(2)}x  (saved ${s - p} ms)`);
		}

		const findings = chosen?.findings ?? [];
		log(`\n=== RECONCILE (chief) ===`);
		let decisions = [];
		if (!dryRun && findings.length) {
			const c = await runChief(client, findings);
			decisions = sanitizeDecisions(c.decisions, findings);
			log(`  chief returned ${c.decisions.length} decision(s) in ${ms(c.duration)}ms`);
		}
		if (!decisions.length && findings.length) {
			decisions = sanitizeDecisions(fallbackDecisions(findings), findings);
			log(`  using deterministic fallback (${decisions.length} decisions)`);
		}
		for (const d of decisions) log(`    #${d.finding_index} ${d.action}${d.transform !== 'none' ? ` via ${d.transform}` : ''} — ${String(d.reasoning ?? '').slice(0, 90)}`);

		log(`\n=== REPAIR (allow-listed transforms only) ===`);
		const repaired = applyRepairs({ header: ds.header, rows: ds.rows, decisions, findings, cfg });
		log(`  applied ${repaired.applied.length} decision(s), ${repaired.audit.length} change(s), ${repaired.tombstoned} row(s) merged away`);
		for (const r of repaired.rejected) log(`  ! rejected: ${r.reason}`);

		log(`\n=== VERIFY ===`);
		const v = verify({ originalHeader: ds.header, originalRows: ds.rows, repaired, beforeScore: ds.score, cfg });
		for (const i of v.invariants) log(`  ${i.ok ? 'PASS' : 'FAIL'} ${i.name} — ${i.detail}`);
		log(`  health score: ${v.beforeScore} -> ${v.afterScore}${v.rollback_triggered ? `  (ROLLED BACK; attempted ${v.attemptedScore})` : ''}`);

		const header = v.header.includes('__review_flags') ? v.header : [...v.header, '__review_flags'];
		writeFileSync('out/cleaned.csv', toCSV(header, v.rows));
		const review = decisions.filter((d) => d.action === 'flag_for_review').map((d) => ({ ...d, finding: findings[d.finding_index] }));
		const report = {
			run_id: runId, mode_used_for_findings: chosen?.mode ?? null, timings,
			before_score: v.beforeScore, after_score: v.afterScore,
			rollback_triggered: v.rollback_triggered, invariants: v.invariants,
			total_findings: findings.length,
			auto_fixed: decisions.filter((d) => d.action === 'auto_fix').length,
			flagged: review.length, ignored: decisions.filter((d) => d.action === 'ignore').length,
			findings, decisions, audit_trail: repaired.audit,
			rejected_decisions: repaired.rejected, review_queue: review,
		};
		writeFileSync('out/evidence_report.json', JSON.stringify(report, null, 2));
		// Archive per run so the console can show PAST results, not just the last.
		mkdirSync('out/runs', { recursive: true });
		writeFileSync(`out/runs/${runId}.json`, JSON.stringify(report, null, 2));
		writeFileSync(`out/runs/${runId}.csv`, toCSV(header, v.rows));

		await hot.log_event('telemetry', telemetryEvent({
			run_id: runId, agent: 'RUN', mode: chosen?.mode ?? modeArg, duration_ms: timings.reduce((a, t) => a + t.duration_ms, 0),
			outcome: v.rollback_triggered ? 'rolled_back' : 'ok',
			note: `findings=${findings.length} fixed=${report.auto_fixed} flagged=${report.flagged} ignored=${report.ignored} ${v.beforeScore}->${v.afterScore}`,
		}));

		// Publish to the cloud file store so the dashboard app reads it live.
		if (client) {
			try {
				const pub = await publishTelemetry(client, hot.events ?? [], {
					run_id: runId, finished_at: new Date().toISOString(),
					timings, before_score: v.beforeScore, after_score: v.afterScore,
					rollback_triggered: v.rollback_triggered,
					total_findings: report.total_findings, auto_fixed: report.auto_fixed,
					flagged: report.flagged, ignored: report.ignored,
					rows_before: ds.rows.length, rows_after: v.rows.length,
					dataset: csvPath,
				});
				log(`  telemetry published -> ${pub.path} (${pub.events} events, ${pub.runs} runs)`);
			} catch (e) { log(`  ! telemetry publish failed: ${String(e.message).slice(0, 120)}`); }
		}

		const leaked = hot.openDatabases();
		log(`\n  leaked Hotdata databases: ${leaked.length}${leaked.length ? ` -> ${leaked.join(', ')}` : ' (none — create/destroy balanced)'}`);
		log(`\nwrote out/cleaned.csv and out/evidence_report.json`);
	} finally {
		if (client) await client.disconnect().catch(() => {});
	}
}

main().catch((e) => { console.error('FATAL:', e); process.exit(1); });
