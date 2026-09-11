/**
 * The three specialist definitions — SHARED, mode-agnostic.
 *
 * This is the single source of truth for specialist logic. Both the parallel
 * pipeline and the sequential pipelines are generated from this array, so the
 * spec's "do not duplicate the specialist logic between modes" holds by
 * construction: only the wiring differs (src/genpipe.mjs), never the content.
 */

/** Findings contract every specialist must emit. Kept in one place so the
 *  three prompts, the chief agent and the repair engine agree on the shape. */
export const FINDING_SHAPE = `{
  "finding_type": "<short_snake_case_kind>",
  "severity": "low" | "medium" | "high",
  "affected_columns": ["<column name>", ...],
  "affected_rows": [<0-based row index>, ...],
  "evidence": "<one sentence citing concrete values you saw>",
  "proposed_action": "trim_normalize_whitespace" | "standardize_date_format" |
                     "fill_null_with" | "merge_duplicate_rows" | "flag_outlier" | "none"
}`;

const OUTPUT_CONTRACT = `Return ONLY a JSON object, no prose and no markdown fence:
{"agent": "<YOUR_AGENT_ID>", "findings": [ ${FINDING_SHAPE} ]}
If you find nothing, return {"agent": "<YOUR_AGENT_ID>", "findings": []}.
Never invent a row index or column name that is not in the data you were given.

Output rules — these are strict:
- Your reply must START with { and END with }. Nothing before, nothing after.
- Do NOT narrate, do NOT explain your reasoning, do NOT write "Here's a thinking process".
- Do NOT wrap the JSON in markdown fences.`;

export const SPECIALISTS = [
	{
		id: 'SCHEMA_MD',
		nodeKey: 'schema',
		title: 'Schema specialist',
		/** Which columns this specialist is allowed to see — its isolated slice. */
		slice: 'schema',
		role: 'You are SCHEMA_MD, a data-quality specialist that audits structure only.',
		instructions: [
			'Check for: null / empty / placeholder values ("", "NA", "null", "-").',
			'Check for: type mismatches within a column (a number column holding text, etc).',
			'Check for: inconsistent formats in one column — especially dates written several ways (2024-01-05 vs 01/05/2024 vs Jan 5 2024).',
			'Check for: schema drift — a column whose values stop matching the shape the rest of the column follows.',
			'Use finding_type values like: null_values, type_mismatch, inconsistent_date_format, schema_drift.',
			'Propose fill_null_with for nulls, standardize_date_format for mixed dates, trim_normalize_whitespace for stray whitespace.',
			'Do NOT report duplicates or numeric outliers — other specialists own those.',
		],
	},
	{
		id: 'DUPLICATE_MD',
		nodeKey: 'duplicate',
		title: 'Duplicate specialist',
		slice: 'text',
		role: 'You are DUPLICATE_MD, a data-quality specialist that finds duplicate and near-duplicate records.',
		instructions: [
			'Normalise text before comparing: trim, collapse inner whitespace, casefold, ignore punctuation.',
			'Find exact duplicate rows AND near-duplicates (same person/entity written differently: "Jon Smith" vs "jon  smith", "ACME Inc" vs "Acme, Inc.").',
			'Group candidates: every finding should list ALL row indices in the duplicate group in affected_rows.',
			'Do not flag a row as duplicate merely because one shared field matches — require the row to plausibly describe the same entity.',
			'Use finding_type values like: exact_duplicate, fuzzy_duplicate.',
			'Propose merge_duplicate_rows for groups you are confident about; propose "none" when it may be a legitimate re-entry and let the chief agent decide.',
			'Do NOT report nulls, formats or numeric outliers — other specialists own those.',
		],
	},
	{
		id: 'ANOMALY_MD',
		nodeKey: 'anomaly',
		title: 'Anomaly specialist',
		slice: 'numeric',
		role: 'You are ANOMALY_MD, a data-quality specialist that finds statistical and business-rule outliers in numeric data.',
		instructions: [
			'For each numeric column compute quartiles and flag values outside [Q1 - k*IQR, Q3 + k*IQR].',
			'Also flag values outside the configured business ranges you are given, even when they sit inside the IQR fence.',
			'Report the actual offending value in evidence — never just "an outlier was found".',
			'Use finding_type values like: statistical_outlier, business_range_violation.',
			'Propose flag_outlier — NEVER propose mutating an outlier. Outliers are tagged for human review, not silently changed.',
			'Do NOT report nulls, formats or duplicates — other specialists own those.',
		],
	},
];

/** Build the full instruction block for one specialist (shared by both modes). */
export function specialistPrompt(spec, cfg) {
	const extra =
		spec.id === 'ANOMALY_MD'
			? [
					`IQR multiplier k = ${cfg.anomaly.iqrMultiplier}.`,
					`Business ranges (column -> allowed min/max): ${JSON.stringify(cfg.anomaly.businessRanges)}.`,
				]
			: [];
	return [
		spec.role,
		'',
		...spec.instructions.map((l) => `- ${l}`),
		...extra.map((l) => `- ${l}`),
		'',
		OUTPUT_CONTRACT.replace(/<YOUR_AGENT_ID>/g, spec.id),
	].join('\n');
}

export const byId = Object.fromEntries(SPECIALISTS.map((s) => [s.id, s]));
