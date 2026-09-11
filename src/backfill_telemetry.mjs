/** Push whatever telemetry exists locally into the cloud file store, so the
 *  dashboard has live data even before the next full run. */
import { readFileSync, existsSync } from 'node:fs';
import { RocketRideClient } from 'rocketride';
import { publishTelemetry } from './publish_telemetry.mjs';

const events = existsSync('data/telemetry.jsonl')
	? readFileSync('data/telemetry.jsonl', 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l))
	: [];

// Reconstruct one summary per run_id from the RUN rows the harness emits.
const runs = [];
for (const e of events.filter((e) => e.agent === 'RUN')) {
	const m = /findings=(\d+) fixed=(\d+) flagged=(\d+) ignored=(\d+) ([\d.]+)->([\d.]+)/.exec(e.note ?? '');
	const peers = events.filter((x) => x.run_id === e.run_id && x.agent !== 'RUN');
	const timings = [...new Set(peers.map((p) => p.mode))].map((mode) => ({
		mode,
		duration_ms: Math.max(...peers.filter((p) => p.mode === mode).map((p) => p.duration_ms || 0)) || null,
	}));
	runs.push({
		run_id: e.run_id, finished_at: e.ts, timings,
		before_score: m ? Number(m[5]) : 0, after_score: m ? Number(m[6]) : 0,
		rollback_triggered: e.outcome === 'rolled_back',
		total_findings: m ? Number(m[1]) : 0, auto_fixed: m ? Number(m[2]) : 0,
		flagged: m ? Number(m[3]) : 0, ignored: m ? Number(m[4]) : 0,
		rows_before: 12, rows_after: 12 - (m ? Number(m[2]) > 0 ? 1 : 0 : 0),
		dataset: 'data/sample.csv',
	});
}

const client = new RocketRideClient({ uri: process.env.ROCKETRIDE_URI, auth: process.env.ROCKETRIDE_APIKEY });
await client.connect();
let last = null;
for (const r of runs) last = await publishTelemetry(client, events.filter((e) => e.run_id === r.run_id), r);
console.log('backfilled:', JSON.stringify(last), '| runs:', runs.length, '| events:', events.length);
const check = await client.fsReadJson('smoky/telemetry.json');
console.log('verified in store -> events:', check.events.length, 'runs:', check.runs.length);
await client.disconnect();
