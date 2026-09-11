/**
 * Isolate the Hotdata variable: ONE specialist, one ephemeral database.
 * Three agents in parallel each doing load->inspect->query is what exceeded
 * 300s; a single agent is the cheapest honest test of the lifecycle.
 */
import { readFileSync } from 'node:fs';
import { RocketRideClient, Question } from 'rocketride';
import { buildSequential } from './src/genpipe.mjs';
import { parseCSV } from './src/csv.mjs';
import { extractJSON, answersOf, answerText } from './src/parse.mjs';

const cfg = JSON.parse(readFileSync('config/dataer.config.json', 'utf8'));
cfg.hotdata.enabled = true;          // force on for this test only
cfg.run.maxWaves = 4;

const { header, rows } = parseCSV(readFileSync('data/sample.csv', 'utf8'));
const { spec, pipeline } = buildSequential(cfg)[0];      // SCHEMA_MD
const hd = pipeline.components.filter((c) => c.provider === 'db_hotdata');
console.log(`pipeline: ${pipeline.components.length} nodes | db_hotdata: ${hd.map((c) => c.id + '/' + c.config.table).join(',')}`);

const c = new RocketRideClient({
	uri: process.env.ROCKETRIDE_URI, auth: process.env.ROCKETRIDE_APIKEY, persist: true,
});
await c.connect();

// Watch engine events so we can SEE the create/query/destroy, not infer it.
const seen = [];
c.onEvent = async (m) => { seen.push(m); };
try { await c.addMonitor({ token: '*' }, ['*']); } catch { /* best effort */ }

const v = await c.validate({ pipeline });
console.log('validate:', v.errors?.length ? JSON.stringify(v.errors) : 'OK');

const t0 = performance.now();
const { token } = await c.use({ pipeline, ttl: 900, threads: 2, name: 'hotdata-isolation-test' });
console.log('token', token, '- waiting (up to 10 min)…');
try {
	const q = new Question();
	q.addQuestion([
		`Diagnose this dataset as ${spec.id}.`,
		'',
		`Dataset (${rows.length} rows), 0-based __row index before each colon:`,
		rows.map((r, i) => `${i}: ${header.map((h) => `${h}=${JSON.stringify(r[h])}`).join(', ')}`).join('\n'),
		'',
		'Now return your findings JSON.',
	].join('\n'));
	const res = await c.chat({ token, question: q });
	const a = answersOf(res)[0];
	const parsed = extractJSON(a);
	console.log(`ELAPSED ${Math.round(performance.now() - t0)}ms`);
	console.log('findings:', parsed?.findings?.length ?? 'PARSE FAIL');
	console.log('raw:', answerText(a).slice(0, 900));
} catch (e) {
	console.log(`FAILED after ${Math.round(performance.now() - t0)}ms:`, String(e.message).slice(0, 200));
} finally { await c.terminate(token).catch(() => {}); }

const hits = seen.filter((m) => /hotdata|load_data|execute|sql/i.test(JSON.stringify(m)));
console.log(`events captured: ${seen.length} | hotdata-related: ${hits.length}`);
for (const h of hits.slice(0, 8)) console.log('  ', JSON.stringify(h).slice(0, 240));
await c.disconnect().catch(() => {});
