/**
 * Answer parsing.
 *
 * Components differ in what they put on the `answers` lane: agent_rocketride
 * returns a JSON *string*, while a plain LLM with `expectJson` can return an
 * already-parsed *object*. Coercing with String() destroys the latter
 * ("[object Object]"), so handle both shapes explicitly.
 */

/** Pull a JSON object out of an answer that may be an object, or text that is
 *  fenced or chatty. */
export function extractJSON(value) {
	if (value == null) return null;
	if (typeof value === 'object') {
		// Already structured. Some providers nest the payload one level.
		if (Array.isArray(value)) return value.length === 1 ? extractJSON(value[0]) : value;
		if (Array.isArray(value.findings) || Array.isArray(value.decisions)) return value;
		for (const k of ['answer', 'result', 'output', 'json', 'content', 'text']) {
			if (value[k] != null) {
				const inner = extractJSON(value[k]);
				if (inner) return inner;
			}
		}
		return value;
	}
	const s = String(value);
	const fence = s.match(/```(?:json)?\s*([\s\S]*?)```/i);
	for (const c of [fence?.[1], s]) {
		if (!c) continue;
		try { return JSON.parse(c.trim()); } catch { /* fall through */ }
		const a = c.indexOf('{'), b = c.lastIndexOf('}');
		if (a >= 0 && b > a) { try { return JSON.parse(c.slice(a, b + 1)); } catch { /* fall through */ } }
	}
	return null;
}

/** answers is string[] | object[] — one entry per agent in a fan-out. Return
 *  the entries UNCOERCED so extractJSON can see objects as objects. */
export function answersOf(result) {
	const a = result?.answers;
	if (a == null) return [];
	return Array.isArray(a) ? a : [a];
}

/** Human-readable form of one answer, for logs. */
export function answerText(value) {
	return typeof value === 'object' ? JSON.stringify(value) : String(value);
}
