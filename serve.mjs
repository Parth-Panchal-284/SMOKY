#!/usr/bin/env node
/**
 * Keep the diagnosis pipeline UP so an external frontend can call it over HTTP.
 *
 * Webhook endpoints exist ONLY while their pipeline is running, so a frontend
 * needs a long-lived task. Started with ttl: 0 (no idle timeout) the task keeps
 * running on the RocketRide server after this process exits — pipelines run
 * server-side, the client is only a remote control.
 *
 *   node --env-file=.env serve.mjs            # start (or report) the endpoint
 *   node --env-file=.env serve.mjs --status   # is it up?
 *   node --env-file=.env serve.mjs --stop     # tear it down
 */
import { readFileSync } from 'node:fs';
import { RocketRideClient } from 'rocketride';

const PIPE = 'pipelines/diagnosis_webhook.pipe';
const argv = process.argv.slice(2);
const flag = (k) => argv.includes(`--${k}`);

const pipeline = JSON.parse(readFileSync(PIPE, 'utf8'));
const projectId = pipeline.project_id;
const sourceId = pipeline.source;

const client = new RocketRideClient({ uri: process.env.ROCKETRIDE_URI, auth: process.env.ROCKETRIDE_APIKEY });
await client.connect();

/** Find an already-running task for this project, if any. */
async function findRunning() {
	try {
		const { rows = [] } = await client.listTasks({ page: 1, page_size: 100 });
		return rows.find((r) => r.projectId === projectId) ?? null;
	} catch { return null; }
}

const httpBase = String(process.env.ROCKETRIDE_URI || '').replace(/^ws/, 'http').replace(/:443$/, '');
const webhookUrl = `${httpBase}/webhook/${projectId}/${sourceId}`;

if (flag('status')) {
	const t = await findRunning();
	console.log(t ? `UP   ${t.id}  (${t.name})` : 'DOWN (no task for this project)');
	console.log('url:', webhookUrl);
	await client.disconnect();
	process.exit(t ? 0 : 1);
}

if (flag('stop')) {
	const t = await findRunning();
	if (!t) { console.log('nothing running for this project'); }
	else {
		const tok = await client.getTaskToken({ projectId, source: sourceId }).catch(() => undefined);
		if (tok) { await client.terminate(tok); console.log('terminated', tok); }
		else console.log('found task', t.id, 'but could not resolve its token — stop it from the IDE task monitor');
	}
	await client.disconnect();
	process.exit(0);
}

// ---- start ----
const existing = await findRunning();
if (existing) {
	console.log('already running:', existing.id);
} else {
	// ttl: 0 => no idle timeout, so the task outlives this process.
	const res = await client.use({
		pipeline, ttl: 0, threads: 4, name: 'smoky-webhook-endpoint',
	});
	console.log('started task token:', res.token);
	// The start response may carry the generated webhook credentials.
	const creds = Object.fromEntries(
		Object.entries(res).filter(([k, v]) => typeof v === 'string' && /^(pk_|tk_)/.test(v) || /url|key|token/i.test(k)),
	);
	if (Object.keys(creds).length) console.log('credentials from start response:', JSON.stringify(creds, null, 2));
}

console.log('');
console.log('=== ENDPOINT FOR YOUR FRONTEND ===');
console.log('POST', webhookUrl);
console.log('Authorization: <your account API key, or a pk_ token>');
console.log('Content-Type: application/json');
console.log('');
console.log('curl -X POST "' + webhookUrl + '" \\');
console.log('     -H "Authorization: $ROCKETRIDE_APIKEY" \\');
console.log("     -H 'Content-Type: application/json' \\");
console.log(`     -d '{"question":"Diagnose this dataset","rows":[{"id":1,"name":"Jon Smith"}]}'`);
console.log('');
console.log('Response keys come from the pipeline response nodes: { answers: [...] }');
await client.disconnect();
