/**
 * Hotdata interface — the seam between the RocketRide half and the Hotdata half.
 *
 * ============================ FOR THE HOTDATA OWNER ============================
 * Implement `RealHotdata` below. Everything else in this repo already calls
 * through this interface, so nothing else has to change.
 *
 * IMPORTANT ARCHITECTURAL NOTE — read before implementing:
 *   RocketRide pipelines execute ON THE SERVER (staging.rocketride.ai), not on
 *   this laptop. A Hotdata endpoint on localhost is therefore NOT reachable
 *   from inside a running pipeline. There are two integration points, and they
 *   are different:
 *
 *   (a) IN-PIPELINE (create -> query -> destroy per specialist).
 *       Handled natively by the `db_hotdata` pipeline component — it creates one
 *       ephemeral database per run, lets the agent inspect its live schema and
 *       run read-only SQL, and destroys it at teardown. Turn it on by setting
 *       hotdata.enabled = true in config/smoky.config.json and supplying
 *       ROCKETRIDE_HOTDATA_KEY + ROCKETRIDE_HOTDATA_WORKSPACE in .env.
 *       => create_db / query / destroy_db below are then NO-OPS in the harness:
 *          the pipeline is doing it. They stay here to keep the audit shape.
 *
 *   (b) HOST-SIDE TELEMETRY (the persistent cross-session DB).
 *       That is `log_event`, and it must be a real, reachable Hotdata database
 *       that survives every run — this is the one the demo dashboard queries
 *       live. Implement it against the Hotdata HTTP API from this process.
 * ==============================================================================
 */

/** Event schema — locked down early so both halves write the same rows. */
export function telemetryEvent({ run_id, agent, mode, query_count = 0, duration_ms, outcome, cost = 0, note = '' }) {
	return {
		run_id, agent, mode,
		query_count, duration_ms, outcome, cost, note,
		ts: new Date().toISOString(),
	};
}

/** Mock used until the real Hotdata layer lands. Keeps everything in memory
 *  plus an on-disk JSONL so cross-session comparison still demos. */
export class MockHotdata {
	constructor({ jsonlPath = 'data/telemetry.jsonl' } = {}) {
		this.jsonlPath = jsonlPath;
		this.dbs = new Map();
		this.events = [];
		this._seenRuns = new Set();
	}
	async create_db(agent_id, slice) {
		const db_id = `mock_${agent_id}_${Math.random().toString(36).slice(2, 8)}`;
		this.dbs.set(db_id, { agent_id, slice, created: Date.now() });
		return db_id;
	}
	async query(db_id, query_type, query) {
		if (!this.dbs.has(db_id)) throw new Error(`unknown db ${db_id}`);
		return { rows: [], note: 'MockHotdata: no query engine; specialists analyse the slice passed in context.' };
	}
	async destroy_db(db_id) { this.dbs.delete(db_id); }

	/** Idempotent per (run_id, agent, outcome) so a re-run cannot corrupt
	 *  cross-session comparisons — the spec's idempotency requirement. */
	async log_event(_telemetry_db_id, event) {
		const key = `${event.run_id}|${event.agent}|${event.outcome}|${event.mode}`;
		if (this._seenRuns.has(key)) return false;
		this._seenRuns.add(key);
		this.events.push(event);
		const { appendFileSync, mkdirSync } = await import('node:fs');
		const { dirname } = await import('node:path');
		mkdirSync(dirname(this.jsonlPath), { recursive: true });
		appendFileSync(this.jsonlPath, JSON.stringify(event) + '\n');
		return true;
	}
	async ensure_telemetry_db() { return 'mock_telemetry_db'; }
	/** Leaked DBs are a bug — the harness asserts this is empty at the end. */
	openDatabases() { return [...this.dbs.keys()]; }
}

/** TODO(hotdata-owner): implement against the real Hotdata API. */
export class RealHotdata {
	constructor({ apiKey, workspaceId, apiUrl = 'https://api.hotdata.dev' } = {}) {
		this.apiKey = apiKey; this.workspaceId = workspaceId; this.apiUrl = apiUrl;
	}
	// TODO: POST /databases  -> { db_id }. Set an expires_at so a crashed run cannot leak a DB.
	async create_db(_agent_id, _slice) { throw new Error('RealHotdata.create_db not implemented'); }
	// TODO: POST /databases/:id/query with query_type sql|vector|fulltext -> QueryResult
	async query(_db_id, _query_type, _query) { throw new Error('RealHotdata.query not implemented'); }
	// TODO: DELETE /databases/:id
	async destroy_db(_db_id) { throw new Error('RealHotdata.destroy_db not implemented'); }
	// TODO: INSERT one row into the PERSISTENT telemetry DB (never per-run).
	//       Must be idempotent on (run_id, agent, outcome, mode).
	async log_event(_telemetry_db_id, _event) { throw new Error('RealHotdata.log_event not implemented'); }
	// TODO: create the persistent telemetry DB once, at the very start, and return its id.
	async ensure_telemetry_db() { throw new Error('RealHotdata.ensure_telemetry_db not implemented'); }
	openDatabases() { return []; }
}

/**
 * Single swap point.
 *
 * IMPORTANT: `hotdata.enabled` controls the IN-PIPELINE integration only — it
 * makes the generator wire one db_hotdata node per specialist, and the engine
 * handles create/query/destroy server-side. It says nothing about this
 * host-side telemetry sink, which is a separate concern (a persistent
 * cross-session database, not a per-run ephemeral one).
 *
 * Conflating the two meant turning on the pipeline integration also swapped
 * telemetry to the unimplemented RealHotdata stub, which killed the run before
 * a single pipeline started. Gate the sink on its own flag.
 */
export function makeHotdata(cfg, env = process.env) {
	const useReal = cfg.hotdata.useRealTelemetrySink === true && env.ROCKETRIDE_HOTDATA_KEY;
	if (useReal)
		return new RealHotdata({
			apiKey: env.ROCKETRIDE_HOTDATA_KEY,
			workspaceId: env.ROCKETRIDE_HOTDATA_WORKSPACE,
		});
	return new MockHotdata();
}
