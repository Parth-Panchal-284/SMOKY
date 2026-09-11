/** Build each specialist's isolated data slice — it only ever sees its own. */
import { isNumeric, isNullish } from './profile.mjs';

export function buildSlice(spec, header, rows, profile) {
	const numericCols = header.filter((h) => profile.columns[h].numericRatio >= 0.6);
	const textCols = header.filter((h) => !numericCols.includes(h));
	let cols;
	if (spec.slice === 'numeric') cols = [...new Set([...numericCols, ...profile.identityColumns])];
	else if (spec.slice === 'text') cols = [...new Set([...textCols, ...profile.identityColumns])];
	else cols = header;                                  // schema specialist sees structure of everything
	return {
		columns: cols,
		rows: rows.map((r, i) => ({ __row: i, ...Object.fromEntries(cols.map((c) => [c, r[c]])) })),
	};
}
