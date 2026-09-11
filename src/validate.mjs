import { readFileSync, readdirSync } from 'node:fs';
import { RocketRideClient } from 'rocketride';
import { buildParallel } from './genpipe.mjs';

const client = new RocketRideClient({ uri: process.env.ROCKETRIDE_URI, auth: process.env.ROCKETRIDE_APIKEY });
await client.connect();
let bad = 0;
for (const f of readdirSync('pipelines').filter((f) => f.endsWith('.pipe'))) {
	const pipeline = JSON.parse(readFileSync(`pipelines/${f}`, 'utf8'));
	const r = await client.validate({ pipeline });
	const ok = !r.errors?.length;
	if (!ok) bad++;
	console.log(`${ok ? 'OK  ' : 'FAIL'} ${f}`, ok ? '' : JSON.stringify(r.errors), r.warnings?.length ? `warnings=${JSON.stringify(r.warnings)}` : '');
}
// also validate the hotdata-enabled variant so the flag is proven, not assumed
const cfg = JSON.parse(readFileSync('config/smoky.config.json', 'utf8'));
cfg.hotdata.enabled = true;
const hd = await client.validate({ pipeline: buildParallel(cfg) });
console.log(`${hd.errors?.length ? 'FAIL' : 'OK  '} diagnosis.pipe [hotdata.enabled=true]`, hd.errors?.length ? JSON.stringify(hd.errors) : '');
await client.disconnect();
process.exit(bad || hd.errors?.length ? 1 : 0);
