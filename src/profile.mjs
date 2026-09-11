/**
 * Deterministic profiler — the SAME code computes the intake "before" score
 * and the verification gate's "after" score, so the two numbers are
 * genuinely comparable (the spec requires re-running the intake scoring).
 */
const NULLISH = new Set(['', 'na', 'n/a', 'null', 'none', '-', '?']);

export const isNullish = (v) => NULLISH.has(String(v ?? '').trim().toLowerCase());
export const isNumeric = (v) => !isNullish(v) && Number.isFinite(Number(String(v).trim()));

const DATE_SHAPES = [
	[/^\d{4}-\d{2}-\d{2}$/, 'YYYY-MM-DD'],
	[/^\d{1,2}\/\d{1,2}\/\d{4}$/, 'MM/DD/YYYY'],
	[/^[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}$/, 'MON D YYYY'],
];
export function dateShape(v) {
	const s = String(v ?? '').trim();
	for (const [re, name] of DATE_SHAPES) if (re.test(s)) return name;
	return null;
}
export const normText = (v) => String(v ?? '').trim().toLowerCase().replace(/\s+/g, ' ').replace(/[.,]/g, '');

export function profileTable(header, rows) {
	const columns = {};
	for (const h of header) {
		const vals = rows.map((r) => r[h]);
		const nulls = vals.filter(isNullish).length;
		const nums = vals.filter(isNumeric).length;
		const shapes = new Set(vals.map(dateShape).filter(Boolean));
		columns[h] = {
			nullCount: nulls,
			nullRatio: rows.length ? nulls / rows.length : 0,
			numericRatio: rows.length ? nums / rows.length : 0,
			distinct: new Set(vals.map((v) => String(v).trim())).size,
			dateShapes: [...shapes],
			mixedDateFormats: shapes.size > 1,
			allEmpty: nulls === vals.length && vals.length > 0,
		};
	}
	// Duplicate detection ignores surrogate keys: a column whose values are all
	// distinct AND numeric is an identity column, not content. Including it
	// would make every row trivially unique and hide real duplicates.
	const identityCols = header.filter(
		(h) => columns[h].distinct === rows.length && columns[h].numericRatio === 1 && rows.length > 1,
	);
	const contentCols = header.filter((h) => !identityCols.includes(h));
	const seen = new Map();
	const duplicateGroups = [];
	rows.forEach((r, i) => {
		const k = contentCols.map((h) => normText(r[h])).join('|');
		if (seen.has(k)) {
			const g = duplicateGroups.find((g) => g.key === k);
			if (g) g.rows.push(i);
			else duplicateGroups.push({ key: k, rows: [seen.get(k), i] });
		} else seen.set(k, i);
	});
	const dupes = duplicateGroups.reduce((a, g) => a + g.rows.length - 1, 0);
	return {
		rowCount: rows.length,
		columnCount: header.length,
		columns,
		identityColumns: identityCols,
		duplicateGroups,
		exactDuplicateRows: dupes,
	};
}

/** Health score 0-100. Penalises nulls, mixed date formats and duplicates. */
export function healthScore(p) {
	if (!p.rowCount || !p.columnCount) return 0;
	const cols = Object.values(p.columns);
	const nullPenalty = (cols.reduce((a, c) => a + c.nullRatio, 0) / cols.length) * 45;
	const fmtPenalty = (cols.filter((c) => c.mixedDateFormats).length / cols.length) * 25;
	const dupPenalty = (p.exactDuplicateRows / p.rowCount) * 30;
	return Math.max(0, Math.round((100 - nullPenalty - fmtPenalty - dupPenalty) * 10) / 10);
}

export function profileAndScore(header, rows) {
	const p = profileTable(header, rows);
	return { profile: p, score: healthScore(p) };
}
