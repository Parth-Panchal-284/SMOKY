// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * SMOKY Telemetry — live dashboard for the SMOKY multi-agent pipeline.
 *
 * Data path: the harness (run.mjs) publishes every run to the account's cloud
 * file store at `smoky/telemetry.json`; this app polls it over the shell's
 * connection. That is what makes the demo LIVE rather than a screenshot — the
 * numbers move while a run is in flight.
 */

import React from 'react';
import { AppLayout, ContentHeader, Card, Button, useShellConnection } from 'shell';

import { EMPTY, AGENT_COLOR } from './types';
import type { TelemetryPayload, RunSummary, TelemetryEvent } from './types';
import { Stat, ModeBars, AgentBars, HealthTrend, Donut, Empty, fmtMs, NUM } from './charts';
import type { AgentStat, TrendPoint } from './charts';

const TELEMETRY_PATH = 'smoky/telemetry.json';
const POLL_MS = 5000;

// =============================================================================
// DERIVED STATS
// =============================================================================

const lastOf = <T,>(a: T[]): T | null => (a.length ? a[a.length - 1] : null);

function agentStats(events: TelemetryEvent[]): AgentStat[] {
	const byAgent = new Map<string, { total: number; n: number; fail: number }>();
	for (const e of events) {
		if (e.agent === 'RUN' || e.agent === 'WAVE') continue;
		const cur = byAgent.get(e.agent) ?? { total: 0, n: 0, fail: 0 };
		cur.total += e.duration_ms || 0;
		cur.n += 1;
		if (e.outcome !== 'ok') cur.fail += 1;
		byAgent.set(e.agent, cur);
	}
	return [...byAgent.entries()]
		.map(([agent, v]) => ({
			agent,
			avgMs: v.n ? v.total / v.n : 0,
			runs: v.n,
			failures: v.fail,
			color: AGENT_COLOR[agent] ?? 'var(--rr-brand)',
		}))
		.sort((a, b) => b.avgMs - a.avgMs);
}

function modeTimes(run: RunSummary | null): { parallel: number | null; sequential: number | null } {
	const find = (m: string) => run?.timings?.find((t) => t.mode === m)?.duration_ms ?? null;
	return { parallel: find('parallel'), sequential: find('sequential') };
}

/** Best observed speedup across every session, not just the latest. */
function bestSpeedup(runs: RunSummary[]): number | null {
	let best: number | null = null;
	for (const r of runs) {
		const { parallel, sequential } = modeTimes(r);
		if (parallel && sequential) {
			const s = sequential / parallel;
			if (best == null || s > best) best = s;
		}
	}
	return best;
}

// =============================================================================
// PIECES
// =============================================================================

const Pulse: React.FC<{ live: boolean }> = ({ live }) => (
	<span style={{ display: 'inline-flex', alignItems: 'center', gap: 7, fontSize: 11.5, color: 'var(--rr-text-secondary)' }}>
		<span
			style={{
				width: 8,
				height: 8,
				borderRadius: '50%',
				background: live ? 'var(--rr-color-success, #22c55e)' : 'var(--rr-text-disabled, #9ca3af)',
				boxShadow: live ? '0 0 0 3px color-mix(in srgb, var(--rr-color-success, #22c55e) 25%, transparent)' : 'none',
			}}
		/>
		{live ? 'live' : 'offline'}
	</span>
);

const RunTable: React.FC<{ runs: RunSummary[] }> = ({ runs }) => {
	if (!runs.length) return <Empty note="No runs recorded yet — run `node --env-file=.env run.mjs --mode both`." />;
	const cell: React.CSSProperties = { padding: '7px 10px', borderBottom: '1px solid var(--rr-border)', whiteSpace: 'nowrap' };
	const head: React.CSSProperties = {
		...cell,
		fontSize: 10,
		textTransform: 'uppercase',
		letterSpacing: '0.05em',
		color: 'var(--rr-text-secondary)',
		fontWeight: 700,
		position: 'sticky',
		top: 0,
		background: 'var(--rr-bg-paper)',
	};
	return (
		<div style={{ overflowX: 'auto', maxHeight: 300, overflowY: 'auto' }}>
			<table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
				<thead>
					<tr>
						<th style={{ ...head, textAlign: 'left' }}>Run</th>
						<th style={{ ...head, textAlign: 'right' }}>Health</th>
						<th style={{ ...head, textAlign: 'right' }}>Findings</th>
						<th style={{ ...head, textAlign: 'right' }}>Fixed</th>
						<th style={{ ...head, textAlign: 'right' }}>Rows</th>
						<th style={{ ...head, textAlign: 'right' }}>Parallel</th>
						<th style={{ ...head, textAlign: 'right' }}>Sequential</th>
						<th style={{ ...head, textAlign: 'left' }}>State</th>
					</tr>
				</thead>
				<tbody>
					{[...runs].reverse().map((r) => {
						const { parallel, sequential } = modeTimes(r);
						const up = r.after_score >= r.before_score;
						return (
							<tr key={r.run_id}>
								<td style={{ ...cell, ...NUM, color: 'var(--rr-text-secondary)' }}>{r.run_id.replace(/^run_/, '')}</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right' }}>
									<span style={{ color: 'var(--rr-text-secondary)' }}>{r.before_score}</span>
									<span style={{ color: 'var(--rr-text-disabled)' }}> → </span>
									<span style={{ color: up ? 'var(--rr-color-success, #22c55e)' : 'var(--rr-color-error, #ef4444)', fontWeight: 700 }}>
										{r.after_score}
									</span>
								</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right' }}>{r.total_findings}</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right' }}>{r.auto_fixed}</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right', color: 'var(--rr-text-secondary)' }}>
									{r.rows_before}→{r.rows_after}
								</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right' }}>{fmtMs(parallel)}</td>
								<td style={{ ...cell, ...NUM, textAlign: 'right' }}>{fmtMs(sequential)}</td>
								<td style={cell}>
									<span
										style={{
											fontSize: 10,
											fontWeight: 700,
											padding: '2px 7px',
											borderRadius: 4,
											letterSpacing: '0.03em',
											background: r.rollback_triggered ? 'var(--rr-color-error, #ef4444)' : 'var(--rr-accent-faded, rgba(34,197,94,.15))',
											color: r.rollback_triggered ? 'var(--rr-bg-default, #fff)' : 'var(--rr-color-success, #22c55e)',
										}}
									>
										{r.rollback_triggered ? 'ROLLED BACK' : 'VERIFIED'}
									</span>
								</td>
							</tr>
						);
					})}
				</tbody>
			</table>
		</div>
	);
};

// =============================================================================
// ROOT
// =============================================================================

const Content: React.FC = () => {
	const { client, isConnected } = useShellConnection();
	const [data, setData] = React.useState<TelemetryPayload>(EMPTY);
	const [error, setError] = React.useState<string | null>(null);
	const [loading, setLoading] = React.useState(true);
	const [fetchedAt, setFetchedAt] = React.useState<string>('');

	const load = React.useCallback(async () => {
		if (!client) return;
		try {
			const payload = await client.fsReadJson<TelemetryPayload>(TELEMETRY_PATH);
			setData({ events: payload?.events ?? [], runs: payload?.runs ?? [], updated_at: payload?.updated_at ?? '' });
			setError(null);
		} catch (e) {
			// A missing file is the normal pre-first-run state, not an error.
			const msg = e instanceof Error ? e.message : String(e);
			setError(/not found|no such|enoent|does not exist/i.test(msg) ? null : msg);
		} finally {
			setLoading(false);
			setFetchedAt(new Date().toLocaleTimeString());
		}
	}, [client]);

	React.useEffect(() => {
		if (!isConnected || !client) return;
		void load();
		const id = window.setInterval(() => void load(), POLL_MS);
		return () => window.clearInterval(id);
	}, [isConnected, client, load]);

	const runs = data.runs;
	const latest = lastOf(runs);
	const { parallel, sequential } = modeTimes(latest);
	const stats = agentStats(data.events);
	const speedup = bestSpeedup(runs);

	const trend: TrendPoint[] = runs.map((r) => ({
		label: r.run_id.replace(/^run_\d{8}/, '').slice(0, 6) || r.run_id.slice(-6),
		before: r.before_score,
		after: r.after_score,
	}));

	const totalFindings = runs.reduce((a, r) => a + r.total_findings, 0);
	const totalFixed = runs.reduce((a, r) => a + r.auto_fixed, 0);
	const totalFlagged = runs.reduce((a, r) => a + r.flagged, 0);
	const totalIgnored = runs.reduce((a, r) => a + r.ignored, 0);
	const rollbacks = runs.filter((r) => r.rollback_triggered).length;
	const delta = latest ? latest.after_score - latest.before_score : 0;

	return (
		<div style={{ padding: '16px 20px 28px', fontFamily: 'var(--rr-font-family, system-ui)' }}>
			<ContentHeader
				title="SMOKY Telemetry"
				subtitle="Parallel specialist diagnosis · reconcile · repair · verify — live from the RocketRide pipeline"
				actions={
					<span style={{ display: 'inline-flex', alignItems: 'center', gap: 12 }}>
						<Pulse live={isConnected && !error} />
						<Button variant="secondary" small onClick={() => void load()}>
							Refresh
						</Button>
					</span>
				}
			/>

			{error ? (
				<div
					style={{
						margin: '10px 0 14px',
						padding: '9px 12px',
						borderRadius: 7,
						border: '1px solid var(--rr-color-error, #ef4444)',
						color: 'var(--rr-color-error, #ef4444)',
						fontSize: 12,
					}}
				>
					{error}
				</div>
			) : null}

			{/* KPI ROW */}
			<div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', margin: '14px 0 16px' }}>
				<Stat label="Sessions" value={String(runs.length)} delta={fetchedAt ? `polled ${fetchedAt}` : undefined} />
				<Stat
					label="Health now"
					value={latest ? latest.after_score.toFixed(1) : '—'}
					delta={latest ? `${delta >= 0 ? '+' : ''}${delta.toFixed(1)} this run` : undefined}
					tone={delta > 0 ? 'good' : delta < 0 ? 'bad' : 'neutral'}
					spark={runs.map((r) => r.after_score)}
				/>
				<Stat label="Findings" value={String(totalFindings)} delta={`${totalFixed} auto-fixed`} />
				<Stat
					label="Best speedup"
					value={speedup ? `${speedup.toFixed(2)}×` : '—'}
					delta="parallel vs sequential"
					tone={speedup && speedup > 1 ? 'good' : 'neutral'}
				/>
				<Stat
					label="Rollbacks"
					value={String(rollbacks)}
					delta={rollbacks ? 'verification caught a bad repair' : 'all runs verified'}
					tone={rollbacks ? 'warn' : 'good'}
				/>
			</div>

			{/* ROW: mode comparison + findings donut */}
			<div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 14 }}>
				<div style={{ flex: '2 1 340px', minWidth: 300 }}>
					<Card header="Parallel vs sequential" fill>
						<ModeBars parallel={parallel} sequential={sequential} />
					</Card>
				</div>
				<div style={{ flex: '1 1 260px', minWidth: 260 }}>
					<Card header="Finding disposition" fill>
						<Donut fixed={totalFixed} flagged={totalFlagged} ignored={totalIgnored} />
					</Card>
				</div>
			</div>

			{/* ROW: trend + agents */}
			<div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 14 }}>
				<div style={{ flex: '2 1 360px', minWidth: 300 }}>
					<Card header="Health score across sessions" fill>
						<HealthTrend points={trend} />
					</Card>
				</div>
				<div style={{ flex: '1 1 260px', minWidth: 260 }}>
					<Card header="Specialist performance" fill>
						<AgentBars stats={stats} />
					</Card>
				</div>
			</div>

			<Card header="Run history" noBodyPadding>
				<RunTable runs={runs} />
			</Card>

			<div style={{ marginTop: 12, fontSize: 10.5, color: 'var(--rr-text-secondary)' }}>
				Source: <code>{TELEMETRY_PATH}</code> in the cloud file store · polled every {POLL_MS / 1000}s
				{data.updated_at ? ` · published ${new Date(data.updated_at).toLocaleString()}` : ''}
				{loading ? ' · loading…' : ''}
			</div>
		</div>
	);
};

const App: React.FC = () => (
	<AppLayout showStatus>
		<Content />
	</AppLayout>
);

export default App;
