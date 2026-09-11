/** Minimal RFC4180-ish CSV reader/writer — no dependency, handles quotes. */
export function parseCSV(text) {
	const rows = [];
	let field = '', row = [], inQ = false;
	for (let i = 0; i < text.length; i++) {
		const ch = text[i];
		if (inQ) {
			if (ch === '"') { if (text[i + 1] === '"') { field += '"'; i++; } else inQ = false; }
			else field += ch;
		} else if (ch === '"') inQ = true;
		else if (ch === ',') { row.push(field); field = ''; }
		else if (ch === '\n') { row.push(field); rows.push(row); row = []; field = ''; }
		else if (ch !== '\r') field += ch;
	}
	if (field.length || row.length) { row.push(field); rows.push(row); }
	const nonEmpty = rows.filter((r) => r.some((c) => c !== ''));
	const header = nonEmpty.shift() ?? [];
	return { header, rows: nonEmpty.map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? '']))) };
}

export function toCSV(header, rows) {
	const esc = (v) => {
		const s = v == null ? '' : String(v);
		return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
	};
	return [header.join(','), ...rows.map((r) => header.map((h) => esc(r[h])).join(','))].join('\n') + '\n';
}
