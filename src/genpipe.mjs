/**
 * Pipeline generator — emits the .pipe files from the shared specialist defs.
 *
 * Parallel mode : chat -> [agent_a, agent_b, agent_c] -> ONE response_answers
 *                 (Pattern 8 fan-out; the three agents run as one wave)
 * Sequential    : one single-specialist pipe per specialist, run back-to-back
 *                 by the harness. RocketRide has no answers->questions
 *                 converter, so agents cannot be chained inside one pipe;
 *                 serial execution of the same generated nodes is the
 *                 faithful sequential baseline.
 *
 * Both modes are generated from src/specialists.mjs — the specialist logic is
 * never written twice.
 */
import { randomUUID } from 'node:crypto';
import { SPECIALISTS, specialistPrompt } from './specialists.mjs';

const X_SOURCE = 20, X_AGENT = 260, X_RESP = 520;
const Y_TOP = 120, Y_STEP = 260;

/**
 * LLM node for ONE agent — each specialist gets its own model.
 *
 * Heterogeneous by design: a schema check wants raw throughput, fuzzy
 * duplicate grouping wants a long context, anomaly reasoning wants more
 * active parameters. config.llm.agents maps agent id -> model, and the
 * `custom` profile lets us name any Nebius Token Factory routing key.
 * Some models live on a regional endpoint, hence the per-agent baseUrl.
 */
export function llmConfigFor(agentId, cfg) {
	const a = cfg.llm.agents?.[agentId];
	if (!a) throw new Error(`No model configured for agent '${agentId}' (config.llm.agents)`);
	return {
		profile: 'custom',
		custom: {
			apikey: cfg.llm.apikeyVar,
			model: a.model,
			base_url: a.baseUrl ?? cfg.llm.defaultBaseUrl ?? '',
			modelTotalTokens: a.modelTotalTokens ?? 131072,
		},
		parameters: {},
	};
}

function llmNode(id, agentId, cfg, controls, pos) {
	return {
		id,
		provider: cfg.llm.provider,
		config: llmConfigFor(agentId, cfg),
		control: controls,
		ui: { position: pos, measured: { width: 150, height: 66 } },
	};
}

function hotdataNode(id, spec, cfg, agentId, pos) {
	const h = cfg.hotdata;
	return {
		id,
		provider: 'db_hotdata',
		config: {
			type: 'db_hotdata',
			apikey: h.apikeyVar,
			workspace_id: h.workspaceVar,
			api_url: '',
			table: `slice_${spec.nodeKey}`,
			db_description:
				`Isolated ${spec.slice} slice for ${spec.id}. One ephemeral database per run: ` +
				`created when the task starts, queried read-only by the specialist, destroyed at teardown.`,
			ttl: h.ttl,
			allow_execute: h.allow_execute,
			allow_destructive_load: h.allow_destructive_load,
			job_timeout_secs: h.job_timeout_secs,
			async_after_ms: h.async_after_ms,
			max_attempts: h.max_attempts,
			max_execute_rows: h.max_execute_rows,
		},
		control: [{ classType: 'tool', from: agentId }],
		ui: { position: pos, measured: { width: 150, height: 135 } },
	};
}

/** Nodes for one specialist: agent + its llm + its memory (+ its Hotdata DB). */
function specialistNodes(spec, cfg, sourceId, row) {
	const a = `agent_${spec.nodeKey}`;
	const l = `llm_${spec.nodeKey}`;
	const m = `mem_${spec.nodeKey}`;
	const h = `hotdata_${spec.nodeKey}`;
	const y = Y_TOP + row * Y_STEP;

	const agent = {
		id: a,
		provider: 'agent_rocketride',
		config: {
			instructions: specialistPrompt(spec, cfg).split('\n'),
			max_waves: cfg.run.maxWaves,
			parameters: {},
		},
		input: [{ lane: 'questions', from: sourceId }],
		ui: { position: { x: X_AGENT, y }, measured: { width: 150, height: 86 } },
	};

	// agent_rocketride requires exactly one llm and exactly one memory.
	const llmControls = [{ classType: 'llm', from: a }];
	const nodes = [agent];

	if (cfg.hotdata.enabled) {
		// db_hotdata itself requires an llm (min 1) to generate SQL — the same
		// node serves both invokers, one control entry each.
		llmControls.push({ classType: 'llm', from: h });
		nodes.push(hotdataNode(h, spec, cfg, a, { x: X_AGENT, y: y + 320 }));
	}

	nodes.push(llmNode(l, spec.id, cfg, llmControls, { x: X_AGENT, y: y + 160 }));
	nodes.push({
		id: m,
		provider: 'memory_internal',
		config: { type: 'memory_internal' },
		control: [{ classType: 'memory', from: a }],
		ui: { position: { x: X_AGENT + 170, y: y + 160 }, measured: { width: 150, height: 66 } },
	});
	return { nodes, agentId: a };
}

function assemble(specs, cfg) {
	const sourceId = 'chat_1';
	const components = [
		{
			id: sourceId,
			provider: 'chat',
			config: { hideForm: true, mode: 'Source', parameters: {}, type: 'chat' },
			ui: { position: { x: X_SOURCE, y: Y_TOP + 80 }, measured: { width: 150, height: 66 } },
		},
	];
	const agentIds = [];
	specs.forEach((spec, i) => {
		const { nodes, agentId } = specialistNodes(spec, cfg, sourceId, i);
		components.push(...nodes);
		agentIds.push(agentId);
	});

	// Pitfall 9: ONE response node, one input entry per agent.
	components.push({
		id: 'response_findings',
		provider: 'response_answers',
		config: {},
		input: agentIds.map((id) => ({ lane: 'answers', from: id })),
		ui: { position: { x: X_RESP, y: Y_TOP + 80 }, measured: { width: 150, height: 66 } },
	});

	return {
		components,
		source: sourceId,
		project_id: randomUUID(),
		viewport: { x: 0, y: 0, zoom: 1 },
		version: 1,
	};
}

/** All three specialists in one wave. */
export function buildParallel(cfg) {
	return assemble(SPECIALISTS, cfg);
}

/** One pipeline per specialist; the harness runs them back to back. */
export function buildSequential(cfg) {
	return SPECIALISTS.map((s) => ({ spec: s, pipeline: assemble([s], cfg) }));
}
