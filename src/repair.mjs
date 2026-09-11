/**
 * Repair engine — allow-listed deterministic transforms ONLY.
 *
 * Nothing here calls a model. A transform that is not in this table cannot be
 * applied, whatever the chief agent asked for. Every application appends to the
 * audit trail, which is also what makes rollback a real revert (src/verify.mjs).
 */
import { isNullish, isNumeric, normText, dateShape } from './profile.mjs';

/** Parse the three date shapes the profiler recognises into YYYY-MM-DD. */
const MONTHS = { jan:'01',feb:'02',mar:'03',apr:'04',may:'05',jun:'06',jul:'07',aug:'08',sep:'09',oct:'10',nov:'11',dec:'12' };
function toISODate(v) {
	const s = String(v ?? '').trim();
	switch (dateShape(s)) {
		case 'YYYY-MM-DD': return s;
		case 'MM/DD/YYYY': {
			const [m, d, y] = s.split('/');
			return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
		}
		case 'MON D YYYY': {
			const m = s.match(/^([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})$/);
			if (!m) return null;
			const mm = MONTHS[m[1].slice(0, 3).toLowerCase()];
			return mm ? `${m[3]}-${mm}-${m[2].padStart(2, '0')}` : null;
		}
		default: return null;
	}
}

function numericStats(rows, col) {
	const nums = rows.map((r) => r[col]).filter(isNumeric).map(Number).sort((a, b) => a - b);
	if (!nums.length) return null;
	const mid = Math.floor(nums.length / 2);
	return {
		mean: nums.reduce((a, b) => a + b, 0) / nums.length,
		median: nums.length % 2 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2,
	};
}
function modeValue(rows, col) {
	const counts = new Map();
	for (const r of rows) if (!isNullish(r[col])) counts.set(r[col], (counts.get(r[col]) ?? 0) + 1);
	let best = null, n = -1;
	for (const [v, c] of counts) if (c > n) { best = v; n = c; }
	return best;
}

/**
 * THE ALLOW-LIST. Each entry mutates `rows` in place and pushes audit records.
 * Signature: (ctx) => void, ctx = { rows, header, columns, targetRows, cfg, audit, findingId }
 */
export const TRANSFORMS = {
	trim_normalize_whitespace(ctx) {
		const { rows, columns, targetRows, audit, findingId } = ctx;
		for (const i of targetRows) for (const c of columns) {
			const before = rows[i]?.[c];
			if (before == null) continue;
			const after = String(before).trim().replace(/\s+/g, ' ');
			if (after !== before) { rows[i][c] = after; audit.push(rec(i, c, 'trim_normalize_whitespace', before, after, findingId)); }
		}
	},
	standardize_date_format(ctx) {
		const { rows, columns, targetRows, audit, findingId } = ctx;
		for (const i of targetRows) for (const c of columns) {
			const before = rows[i]?.[c];
			if (before == null || isNullish(before)) continue;
			const after = toISODate(before);
			if (after && after !== before) { rows[i][c] = after; audit.push(rec(i, c, 'standardize_date_format', before, after, findingId)); }
		}
	},
	fill_null_with(ctx) {
		const { rows, columns, targetRows, cfg, audit, findingId } = ctx;
		const strategy = cfg.repair.nullFillStrategy;
		for (const c of columns) {
			const stats = numericStats(rows, c);
			let fill;
			if (strategy === 'mean' || strategy === 'median') fill = stats ? round2(stats[strategy]) : null;
			else if (strategy === 'mode') fill = modeValue(rows, c);
			else fill = cfg.repair.constantFill ?? '';
			if (fill == null || fill === '') continue;   // never invent a value we cannot justify
			for (const i of targetRows) {
				const before = rows[i]?.[c];
				if (before != null && isNullish(before)) {
					rows[i][c] = String(fill);
					audit.push(rec(i, c, `fill_null_with:${strategy}`, before, String(fill), findingId));
				}
			}
		}
	},
	merge_duplicate_rows(ctx) {
		const { rows, header, targetRows, cfg, audit, findingId } = ctx;
		const group = [...new Set(targetRows)].filter((i) => rows[i]).sort((a, b) => a - b);
		if (group.length < 2) return;
		const completeness = (i) => header.filter((h) => !isNullish(rows[i][h])).length;
		const keep = cfg.repair.duplicateMergeStrategy === 'keep_first'
			? group[0]
			: group.reduce((best, i) => (completeness(i) > completeness(best) ? i : best), group[0]);
		for (const i of group) {
			if (i === keep) continue;
			// backfill anything the kept row is missing before dropping this one
			for (const h of header) if (isNullish(rows[keep][h]) && !isNullish(rows[i][h])) {
				const before = rows[keep][h];
				rows[keep][h] = rows[i][h];
				audit.push(rec(keep, h, 'merge_duplicate_rows:backfill', before, rows[i][h], findingId));
			}
			audit.push({ ...rec(i, '*', 'merge_duplicate_rows:drop', JSON.stringify(rows[i]), null, findingId), dropped: true });
			rows[i] = null;   // tombstone; compacted after all transforms run
		}
	},
	flag_outlier(ctx) {
		const { rows, columns, targetRows, audit, findingId } = ctx;
		for (const i of targetRows) {
			if (!rows[i]) continue;
			const before = rows[i].__review_flags ?? '';
			const tag = `outlier:${columns.join('+')}`;
			if (String(before).includes(tag)) continue;
			const after = before ? `${before};${tag}` : tag;
			rows[i].__review_flags = after;            // NO data mutation — tag only
			audit.push(rec(i, '__review_flags', 'flag_outlier', before, after, findingId));
		}
	},
};

const round2 = (n) => Math.round(n * 100) / 100;
const rec = (row, column, transform_name, before_value, after_value, finding_id) => ({
	row, column, transform_name, before_value, after_value, finding_id, at: new Date().toISOString(),
});

/**
 * Apply the auto_fix decisions. Returns { rows, audit, applied, rejected }.
 * `rejected` records every decision refused because its transform was not
 * allow-listed — that refusal is itself part of the evidence report.
 */
export function applyRepairs({ header, rows, decisions, findings, cfg }) {
	const working = rows.map((r) => ({ ...r }));
	const audit = [];
	const applied = [], rejected = [];
	const allow = new Set(cfg.repair.allowedTransforms);

	for (const d of decisions) {
		if (d.action !== 'auto_fix') continue;
		const f = findings[d.finding_index];
		if (!f) { rejected.push({ ...d, reason: 'finding_index out of range' }); continue; }
		const name = d.transform ?? f.proposed_action;
		if (!allow.has(name) || !TRANSFORMS[name]) {
			rejected.push({ ...d, reason: `transform '${name}' is not allow-listed` });
			continue;
		}
		const targetRows = (f.affected_rows ?? []).filter((i) => Number.isInteger(i) && i >= 0 && i < working.length);
		const columns = (f.affected_columns ?? []).filter((c) => header.includes(c));
		if (!targetRows.length || (!columns.length && name !== 'merge_duplicate_rows')) {
			rejected.push({ ...d, reason: 'finding named no valid rows/columns' });
			continue;
		}
		const before = audit.length;
		TRANSFORMS[name]({ rows: working, header, columns, targetRows, cfg, audit, findingId: d.finding_index });
		applied.push({ ...d, transform_name: name, changes: audit.length - before });
	}

	return { header, rows: working.filter((r) => r !== null), audit, applied, rejected, tombstoned: working.filter((r) => r === null).length };
}

/** Real revert, driven by the audit trail — used by the verification gate. */
export function rollback({ originalHeader, originalRows }) {
	return { header: [...originalHeader], rows: originalRows.map((r) => ({ ...r })) };
}
