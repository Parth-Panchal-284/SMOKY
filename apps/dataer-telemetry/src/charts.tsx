// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/**
 * Hand-rolled SVG visuals for the telemetry dashboard.
 *
 * Everything is inline SVG on --rr-* tokens: no chart library to negotiate
 * through Module Federation, and the shell's theme swap recolours it for free.
 */

import React from 'react';

// =============================================================================
// SHARED
// =============================================================================

export const fmtMs = (ms: number | null | undefined): string => {
	if (ms == null) return '—';
	if (ms < 1000) return `${Math.round(ms)}ms`;
	if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
	return `${Math.floor(ms / 60000)}m ${Math.round((ms % 60000) / 1000)}s`;
};

const NUM: React.CSSProperties = {
	fontVariantNumeric: 'tabular-nums',
	fontFamily: 'var(--rr-font-mono, ui-monospace, Consolas, monospace)',
};

// =============================================================================
// STAT TILE
// =============================================================================

interface StatProps {
	label: string;
	value: string;
	delta?: string;
	tone?: 'neutral' | 'good' | 'warn' | 'bad';
	spark?: number[];
}

const TONE: Record<string, string> = {
	neutral: 'var(--rr-text-primary)',
	good: 'var(--rr-color-success, #22c55e)',
	warn: 'var(--rr-color-warning, #f59e0b)',
	bad: 'var(--rr-color-error, #ef4444)',
};

/** One KPI: big number, optional delta, optional sparkline footer. */
export const Stat: React.FC<StatProps> = ({ label, value, delta, tone = 'neutral', spark }) => (
	<div
		style={{
			flex: '1 1 150px',
			minWidth: 140,
			border: '1px solid var(--rr-border)',
			borderRadius: 10,
			padding: '12px 14px 10px',
			background: 'var(--rr-bg-paper)',
			position: 'relative',
			overflow: 'hidden',
		}}
	>
		<div
			style={{
				fontSize: 10,
				letterSpacing: '0.06em',
				textTransform: 'uppercase',
				color: 'var(--rr-text-secondary)',
				fontWeight: 600,
			}}
		>
			{label}
		</div>
		<div style={{ ...NUM, fontSize: 26, fontWeight: 700, marginTop: 4, color: TONE[tone], lineHeight: 1.1 }}>
			{value}
		</div>
		{delta ? (
			<div style={{ ...NUM, fontSize: 11, color: 'var(--rr-text-secondary)', marginTop: 2 }}>{delta}</div>
		) : null}
		{spark && spark.length > 1 ? (
			<div style={{ marginTop: 8, height: 22 }}>
				<Sparkline values={spark} color={TONE[tone]} />
			</div>
		) : null}
	</div>
);

// =============================================================================
// SPARKLINE
// =============================================================================

export const Sparkline: React.FC<{ values: number[]; color: string }> = ({ values, color }) => {
	const w = 120;
	const h = 22;
	const min = Math.min(...values);
	const max = Math.max(...values);
	const span = max - min || 1;
	const pts = values.map((v, i) => {
		const x = (i / (values.length - 1)) * w;
		const y = h - ((v - min) / span) * (h - 3) - 1.5;
		return `${x.toFixed(1)},${y.toFixed(1)}`;
	});
	return (
		<svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: '100%', height: '100%', display: 'block' }}>
			<polyline points={pts.join(' ')} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" opacity={0.9} />
		</svg>
	);
};

// =============================================================================
// MODE COMPARISON — the headline chart
// =============================================================================

interface ModeBarsProps {
	parallel: number | null;
	sequential: number | null;
}

/** Parallel vs sequential wall-clock, the demo's money shot. */
export const ModeBars: React.FC<ModeBarsProps> = ({ parallel, sequential }) => {
	const max = Math.max(parallel ?? 0, sequential ?? 0, 1);
	const rows: Array<{ k: string; v: number | null; c: string }> = [
		{ k: 'parallel', v: parallel, c: 'var(--rr-chart-green, #22c55e)' },
		{ k: 'sequential', v: sequential, c: 'var(--rr-chart-orange, #f97316)' },
	];
	const speedup = parallel && sequential ? sequential / parallel : null;

	return (
		<div>
			{rows.map(({ k, v, c }) => (
				<div key={k} style={{ marginBottom: 14 }}>
					<div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
						<span style={{ fontSize: 12, fontWeight: 600, color: 'var(--rr-text-primary)', textTransform: 'capitalize' }}>{k}</span>
						<span style={{ ...NUM, fontSize: 12, color: 'var(--rr-text-secondary)' }}>{fmtMs(v)}</span>
					</div>
					<div style={{ height: 22, background: 'var(--rr-bg-surface, rgba(128,128,128,0.12))', borderRadius: 5, overflow: 'hidden' }}>
						<div
							style={{
								width: `${v == null ? 0 : Math.max(2, (v / max) * 100)}%`,
								height: '100%',
								background: `linear-gradient(90deg, ${c}, ${c} 70%, transparent 160%)`,
								borderRadius: 5,
								transition: 'width 600ms cubic-bezier(.22,1,.36,1)',
							}}
						/>
					</div>
				</div>
			))}
			{speedup ? (
				<div
					style={{
						marginTop: 14,
						padding: '10px 12px',
						borderRadius: 8,
						background: 'var(--rr-accent-faded, rgba(34,197,94,0.10))',
						border: '1px solid var(--rr-border)',
						display: 'flex',
						alignItems: 'baseline',
						gap: 8,
						flexWrap: 'wrap',
					}}
				>
					<span style={{ ...NUM, fontSize: 24, fontWeight: 700, color: 'var(--rr-color-success, #22c55e)' }}>
						{speedup.toFixed(2)}×
					</span>
					<span style={{ fontSize: 12, color: 'var(--rr-text-secondary)' }}>
						faster in parallel — saved {fmtMs((sequential ?? 0) - (parallel ?? 0))}
					</span>
				</div>
			) : (
				<div style={{ fontSize: 11.5, color: 'var(--rr-text-secondary)', marginTop: 6 }}>
					Run <code>--mode both</code> to populate the comparison.
				</div>
			)}
		</div>
	);
};

// =============================================================================
// AGENT LEADERBOARD
// =============================================================================

export interface AgentStat {
	agent: string;
	avgMs: number;
	runs: number;
	failures: number;
	color: string;
}

/** Per-specialist duration bars — who is the bottleneck. */
export const AgentBars: React.FC<{ stats: AgentStat[] }> = ({ stats }) => {
	if (!stats.length) return <Empty note="No agent events yet." />;
	const max = Math.max(...stats.map((s) => s.avgMs), 1);
	const slowest = stats.reduce((a, b) => (b.avgMs > a.avgMs ? b : a), stats[0]);
	return (
		<div>
			{stats.map((s) => (
				<div key={s.agent} style={{ marginBottom: 12 }}>
					<div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, gap: 8 }}>
						<span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--rr-text-primary)' }}>
							{s.agent}
							{s.agent === slowest.agent && stats.length > 1 ? (
								<span
									style={{
										marginLeft: 6,
										fontSize: 9.5,
										padding: '1px 5px',
										borderRadius: 4,
										background: 'var(--rr-color-warning, #f59e0b)',
										color: 'var(--rr-bg-default, #fff)',
										fontWeight: 700,
										letterSpacing: '0.03em',
									}}
								>
									BOTTLENECK
								</span>
							) : null}
						</span>
						<span style={{ ...NUM, fontSize: 11.5, color: 'var(--rr-text-secondary)', whiteSpace: 'nowrap' }}>
							{fmtMs(s.avgMs)}
							{s.failures > 0 ? (
								<span style={{ color: 'var(--rr-color-error, #ef4444)' }}> · {s.failures} failed</span>
							) : null}
						</span>
					</div>
					<div style={{ height: 10, background: 'var(--rr-bg-surface, rgba(128,128,128,0.12))', borderRadius: 5, overflow: 'hidden' }}>
						<div
							style={{
								width: `${Math.max(2, (s.avgMs / max) * 100)}%`,
								height: '100%',
								background: s.color,
								borderRadius: 5,
								transition: 'width 600ms cubic-bezier(.22,1,.36,1)',
							}}
						/>
					</div>
				</div>
			))}
		</div>
	);
};

// =============================================================================
// HEALTH TREND — cross-session
// =============================================================================

export interface TrendPoint {
	label: string;
	before: number;
	after: number;
}

/** Before/after health score across sessions — the "is it improving" chart. */
export const HealthTrend: React.FC<{ points: TrendPoint[] }> = ({ points }) => {
	if (points.length < 1) return <Empty note="No completed runs yet." />;
	const w = 620;
	const h = 170;
	const padL = 34;
	const padB = 26;
	const padT = 12;
	const all = points.flatMap((p) => [p.before, p.after]);
	const lo = Math.max(0, Math.floor(Math.min(...all) - 4));
	const hi = Math.min(100, Math.ceil(Math.max(...all) + 4));
	const span = hi - lo || 1;
	const x = (i: number) => padL + (points.length === 1 ? (w - padL - 10) / 2 : (i / (points.length - 1)) * (w - padL - 10));
	const y = (v: number) => padT + (1 - (v - lo) / span) * (h - padT - padB);

	const line = (key: 'before' | 'after') => points.map((p, i) => `${x(i).toFixed(1)},${y(p[key]).toFixed(1)}`).join(' ');
	const areaPts = `${padL},${y(lo)} ${line('after')} ${x(points.length - 1).toFixed(1)},${y(lo)}`;

	return (
		<div style={{ overflowX: 'auto' }}>
			<svg viewBox={`0 0 ${w} ${h}`} style={{ width: '100%', minWidth: 380, height: 'auto', display: 'block' }}>
				<defs>
					<linearGradient id="afterFill" x1="0" y1="0" x2="0" y2="1">
						<stop offset="0%" stopColor="var(--rr-chart-green, #22c55e)" stopOpacity="0.30" />
						<stop offset="100%" stopColor="var(--rr-chart-green, #22c55e)" stopOpacity="0.02" />
					</linearGradient>
				</defs>

				{[0, 0.5, 1].map((f) => {
					const v = lo + f * span;
					return (
						<g key={f}>
							<line x1={padL} y1={y(v)} x2={w - 10} y2={y(v)} stroke="var(--rr-border)" strokeWidth={1} opacity={0.55} />
							<text x={4} y={y(v) + 3.5} fontSize={9} fill="var(--rr-text-secondary)" style={NUM}>
								{v.toFixed(0)}
							</text>
						</g>
					);
				})}

				{points.length > 1 ? <polygon points={areaPts} fill="url(#afterFill)" /> : null}

				<polyline points={line('before')} fill="none" stroke="var(--rr-text-secondary)" strokeWidth={1.6} strokeDasharray="4 3" opacity={0.75} />
				<polyline points={line('after')} fill="none" stroke="var(--rr-chart-green, #22c55e)" strokeWidth={2.4} strokeLinejoin="round" strokeLinecap="round" />

				{points.map((p, i) => (
					<g key={p.label}>
						<circle cx={x(i)} cy={y(p.after)} r={3.4} fill="var(--rr-chart-green, #22c55e)" />
						<circle cx={x(i)} cy={y(p.before)} r={2.4} fill="var(--rr-text-secondary)" opacity={0.8} />
						{i === points.length - 1 || points.length <= 6 ? (
							<text x={x(i)} y={h - 8} fontSize={8.5} fill="var(--rr-text-secondary)" textAnchor="middle" style={NUM}>
								{p.label}
							</text>
						) : null}
					</g>
				))}
			</svg>
			<div style={{ display: 'flex', gap: 16, marginTop: 4, fontSize: 11, color: 'var(--rr-text-secondary)', flexWrap: 'wrap' }}>
				<Legend color="var(--rr-text-secondary)" dashed label="before repair" />
				<Legend color="var(--rr-chart-green, #22c55e)" label="after repair" />
			</div>
		</div>
	);
};

const Legend: React.FC<{ color: string; label: string; dashed?: boolean }> = ({ color, label, dashed }) => (
	<span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
		<svg width={18} height={6} aria-hidden>
			<line x1={0} y1={3} x2={18} y2={3} stroke={color} strokeWidth={2.2} strokeDasharray={dashed ? '4 3' : undefined} />
		</svg>
		{label}
	</span>
);

// =============================================================================
// FINDINGS DONUT
// =============================================================================

export const Donut: React.FC<{ fixed: number; flagged: number; ignored: number }> = ({ fixed, flagged, ignored }) => {
	const total = fixed + flagged + ignored;
	const segs = [
		{ v: fixed, c: 'var(--rr-chart-green, #22c55e)', label: 'auto-fixed' },
		{ v: flagged, c: 'var(--rr-chart-yellow, #eab308)', label: 'flagged' },
		{ v: ignored, c: 'var(--rr-text-disabled, #9ca3af)', label: 'ignored' },
	];
	const R = 52;
	const C = 2 * Math.PI * R;
	let acc = 0;

	return (
		<div style={{ display: 'flex', alignItems: 'center', gap: 18, flexWrap: 'wrap' }}>
			<svg viewBox="0 0 140 140" style={{ width: 132, height: 132, flexShrink: 0 }}>
				<circle cx={70} cy={70} r={R} fill="none" stroke="var(--rr-bg-surface, rgba(128,128,128,0.15))" strokeWidth={17} />
				{total > 0 &&
					segs.map((s) => {
						if (!s.v) return null;
						const frac = s.v / total;
						const el = (
							<circle
								key={s.label}
								cx={70}
								cy={70}
								r={R}
								fill="none"
								stroke={s.c}
								strokeWidth={17}
								strokeDasharray={`${(frac * C).toFixed(2)} ${C.toFixed(2)}`}
								strokeDashoffset={(-acc * C).toFixed(2)}
								transform="rotate(-90 70 70)"
								strokeLinecap="butt"
							/>
						);
						acc += frac;
						return el;
					})}
				<text x={70} y={66} textAnchor="middle" fontSize={26} fontWeight={700} fill="var(--rr-text-primary)" style={NUM}>
					{total}
				</text>
				<text x={70} y={83} textAnchor="middle" fontSize={9} fill="var(--rr-text-secondary)" letterSpacing="0.06em">
					FINDINGS
				</text>
			</svg>
			<div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
				{segs.map((s) => (
					<span key={s.label} style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--rr-text-primary)' }}>
						<span style={{ width: 10, height: 10, borderRadius: 3, background: s.c, flexShrink: 0 }} />
						<span style={{ ...NUM, fontWeight: 700, minWidth: 22 }}>{s.v}</span>
						<span style={{ color: 'var(--rr-text-secondary)' }}>{s.label}</span>
					</span>
				))}
			</div>
		</div>
	);
};

// =============================================================================
// MISC
// =============================================================================

export const Empty: React.FC<{ note: string }> = ({ note }) => (
	<div style={{ fontSize: 12, color: 'var(--rr-text-secondary)', padding: '18px 0', textAlign: 'center' }}>{note}</div>
);

export { NUM };
