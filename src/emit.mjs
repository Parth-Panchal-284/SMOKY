import { writeFileSync, readFileSync } from 'node:fs';
import { buildParallel, buildSequential } from './genpipe.mjs';
import { buildChief } from './genchief.mjs';

const cfg = JSON.parse(readFileSync('config/dataer.config.json', 'utf8'));
const w = (p, o) => { writeFileSync(p, JSON.stringify(o, null, '\t') + '\n'); console.log('wrote', p, `(${o.components.length} nodes)`); };

w('pipelines/diagnosis.pipe', buildParallel(cfg));
for (const { spec, pipeline } of buildSequential(cfg))
	w(`pipelines/diagnosis_seq_${spec.nodeKey}.pipe`, pipeline);
w('pipelines/reconcile_repair.pipe', buildChief(cfg));
