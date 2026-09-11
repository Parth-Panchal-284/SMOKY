/**
 * Pipeline 2 — Reconcile & Repair (`reconcile_repair.pipe`).
 *
 * Only stage 1 (the Chief agent) is LLM work: it reasons about conflicts
 * between specialists. Stages 2 and 3 (repair engine, verification gate) are
 * deterministic host-side code in src/repair.mjs and src/verify.mjs — an
 * allow-listed transform set and a real rollback cannot be delegated to a
 * model and still be auditable. The spec permits the "SDK-code equivalent";
 * this is that choice, made deliberately.
 */
import { randomUUID } from 'node:crypto';
import { llmConfigFor } from './genpipe.mjs';

export const ACTIONS = ['auto_fix', 'flag_for_review', 'ignore'];

export const CHIEF_PROMPT = (cfg) => [
	'You are the CHIEF agent reconciling findings from three data-quality specialists:',
	'SCHEMA_MD (nulls/types/formats), DUPLICATE_MD (duplicate groups), ANOMALY_MD (numeric outliers).',
	'',
	'You will be given their merged findings as JSON. For EVERY finding, decide one action.',
	'',
	'Conflict rules — apply in this order, they are precedence rules and they are binding:',
	'1. If the same row is flagged by DUPLICATE_MD and by ANOMALY_MD, the duplicate takes precedence:',
	'   merging may remove the outlier row entirely. Action the duplicate, and set the anomaly finding to "ignore"',
	'   with reasoning naming the duplicate finding it defers to.',
	'2. If a row is flagged both null (SCHEMA_MD) and duplicate (DUPLICATE_MD), merge first: choose',
	'   merge_duplicate_rows with keep_most_complete, and set the null finding to "ignore".',
	'3. A numeric outlier is NEVER auto_fix. ANOMALY_MD findings are at most flag_for_review.',
	'4. A duplicate group is auto_fix only when the rows agree on every non-empty field they share;',
	'   otherwise flag_for_review — a near-duplicate that disagrees may be a legitimate re-entry.',
	'5. Anything whose proposed_action is not in the allow-list is "flag_for_review", never auto_fix.',
	`   Allow-list: ${cfg.repair.allowedTransforms.join(', ')}.`,
	'6. When you are not confident, prefer flag_for_review over auto_fix. Never prefer ignore to hide uncertainty.',
	'',
	'Return ONLY this JSON, no prose and no markdown fence:',
	'{"decisions":[{"finding_index":<index into the findings array you were given>,',
	'  "agent":"<originating agent id>","action":"auto_fix"|"flag_for_review"|"ignore",',
	'  "transform":"<one allow-listed transform name, or none>",',
	'  "reasoning":"<one sentence, cite the rule number you applied>"}]}',
	'Emit exactly one decision per finding, in the order you were given them.',
];

export function buildChief(cfg) {
	return {
		components: [
			{
				id: 'chat_1',
				provider: 'chat',
				config: { hideForm: true, mode: 'Source', parameters: {}, type: 'chat' },
				ui: { position: { x: 20, y: 200 }, measured: { width: 150, height: 66 } },
			},
			{
				id: 'agent_chief',
				provider: 'agent_rocketride',
				config: { instructions: CHIEF_PROMPT(cfg), max_waves: cfg.run.maxWaves, parameters: {} },
				input: [{ lane: 'questions', from: 'chat_1' }],
				ui: { position: { x: 260, y: 200 }, measured: { width: 150, height: 86 } },
			},
			{
				id: 'llm_chief',
				provider: cfg.llm.provider,
				config: llmConfigFor('CHIEF', cfg),
				control: [{ classType: 'llm', from: 'agent_chief' }],
				ui: { position: { x: 260, y: 360 }, measured: { width: 150, height: 66 } },
			},
			{
				id: 'mem_chief',
				provider: 'memory_internal',
				config: { type: 'memory_internal' },
				control: [{ classType: 'memory', from: 'agent_chief' }],
				ui: { position: { x: 430, y: 360 }, measured: { width: 150, height: 66 } },
			},
			{
				id: 'response_decisions',
				provider: 'response_answers',
				config: {},
				input: [{ lane: 'answers', from: 'agent_chief' }],
				ui: { position: { x: 520, y: 200 }, measured: { width: 150, height: 66 } },
			},
		],
		source: 'chat_1',
		project_id: randomUUID(),
		viewport: { x: 0, y: 0, zoom: 1 },
		version: 1,
	};
}
