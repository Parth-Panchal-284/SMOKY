/**
 * Publish telemetry to the RocketRide cloud file store so the dashboard app can
 * read it LIVE over the shell connection. Without this the dashboard could only
 * show a build-time snapshot — the README requires live queries, not screenshots.
 *
 * Path: dataer/telemetry.json (account-private file store)
 */
export const TELEMETRY_PATH = 'dataer/telemetry.json';

/** Merge new events into whatever is already in the store, de-duplicated. */
export async function publishTelemetry(client, events, summary) {
	let existing = { events: [], runs: [] };
	try { existing = await client.fsReadJson(TELEMETRY_PATH); } catch { /* first write */ }

	const key = (e) => `${e.run_id}|${e.agent}|${e.mode}|${e.outcome}|${e.ts}`;
	const seen = new Set((existing.events ?? []).map(key));
	const merged = [...(existing.events ?? [])];
	for (const e of events) if (!seen.has(key(e))) { seen.add(key(e)); merged.push(e); }

	const runs = [...(existing.runs ?? []).filter((r) => r.run_id !== summary.run_id), summary]
		.sort((a, b) => String(a.finished_at).localeCompare(String(b.finished_at)));

	const payload = { updated_at: new Date().toISOString(), events: merged.slice(-2000), runs: runs.slice(-200) };
	try { await client.fsMkdir('dataer'); } catch { /* exists */ }
	await client.fsWriteJson(TELEMETRY_PATH, payload);
	return { path: TELEMETRY_PATH, events: payload.events.length, runs: payload.runs.length };
}
