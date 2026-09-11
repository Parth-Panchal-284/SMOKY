/**
 * Verification gate — re-score, check invariants, roll the WHOLE batch back on
 * failure. Rollback is a real revert (the pre-repair snapshot restored), not a
 * warning, and the audit trail explains exactly what was undone.
 */
import { profileAndScore, isNullish } from './profile.mjs';
import { rollback } from './repair.mjs';

export function verify({ originalHeader, originalRows, repaired, beforeScore, cfg }) {
	const { profile: afterProfile, score: afterScore } = profileAndScore(repaired.header, repaired.rows);
	const invariants = [];
	const check = (name, ok, detail) => { invariants.push({ name, ok, detail }); return ok; };

	// 1. Row loss is only legitimate via intended dedup, and bounded.
	const lost = originalRows.length - repaired.rows.length;
	const lostRatio = originalRows.length ? lost / originalRows.length : 0;
	const droppedByMerge = repaired.audit.filter((a) => a.dropped).length;
	check('row_loss_explained', lost === droppedByMerge,
		`lost ${lost} row(s); ${droppedByMerge} explained by merge_duplicate_rows`);
	check('row_loss_bounded', lostRatio <= cfg.verification.maxRowLossRatio,
		`lost ${(lostRatio * 100).toFixed(1)}% (limit ${(cfg.verification.maxRowLossRatio * 100).toFixed(0)}%)`);

	// 2. No column may be emptied out by the repairs.
	if (cfg.verification.requireNoEmptyColumns) {
		// Only a column that HAD values before and has none after is a failure —
		// a column that was already empty is not something the repairs broke.
		const wasEmpty = new Set(
			originalHeader.filter((c) => originalRows.every((r) => isNullish(r[c]))),
		);
		const emptied = Object.entries(afterProfile.columns)
			.filter(([c, s]) => s.allEmpty && !wasEmpty.has(c))
			.map(([c]) => c);
		check('no_column_emptied', emptied.length === 0, emptied.length ? `emptied: ${emptied.join(', ')}` : 'none emptied');
	}

	// 3. Repairs must not make the dataset worse.
	if (cfg.verification.requireScoreNotWorse)
		check('score_not_worse', afterScore >= beforeScore,
			`before ${beforeScore} -> after ${afterScore}`);

	// 4. Every applied change must be traceable to a finding.
	check('audit_complete', repaired.audit.every((a) => a.finding_id !== undefined && a.transform_name),
		`${repaired.audit.length} audit record(s)`);

	const failed = invariants.filter((i) => !i.ok);
	if (failed.length) {
		const reverted = rollback({ originalHeader, originalRows });
		return {
			rollback_triggered: true,
			invariants,
			failed: failed.map((f) => f.name),
			beforeScore,
			afterScore: beforeScore,          // reverted, so the score is the original again
			attemptedScore: afterScore,
			header: reverted.header,
			rows: reverted.rows,
			unappliedRepairs: repaired.applied,
		};
	}
	return {
		rollback_triggered: false,
		invariants,
		failed: [],
		beforeScore,
		afterScore,
		header: repaired.header,
		rows: repaired.rows,
		unappliedRepairs: [],
	};
}
