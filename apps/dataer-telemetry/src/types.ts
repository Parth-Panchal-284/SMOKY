// =============================================================================
// MIT License
// Copyright (c) 2026 Aparavi Software AG
// =============================================================================

/** Shapes written by the SMOKY harness (src/publish_telemetry.mjs). */

export interface TelemetryEvent {
	run_id: string;
	agent: string;
	mode: string;
	query_count: number;
	duration_ms: number;
	outcome: string;
	cost: number;
	note: string;
	ts: string;
}

export interface ModeTiming {
	mode: string;
	duration_ms: number | null;
	outcome?: string;
}

export interface RunSummary {
	run_id: string;
	finished_at: string;
	timings: ModeTiming[];
	before_score: number;
	after_score: number;
	rollback_triggered: boolean;
	total_findings: number;
	auto_fixed: number;
	flagged: number;
	ignored: number;
	rows_before: number;
	rows_after: number;
	dataset: string;
}

export interface TelemetryPayload {
	updated_at: string;
	events: TelemetryEvent[];
	runs: RunSummary[];
}

export const EMPTY: TelemetryPayload = { updated_at: '', events: [], runs: [] };

/** The three specialists, in a fixed order so colours stay stable. */
export const AGENTS = ['SCHEMA_MD', 'DUPLICATE_MD', 'ANOMALY_MD'] as const;

export const AGENT_COLOR: Record<string, string> = {
	SCHEMA_MD: 'var(--rr-chart-blue, #3b82f6)',
	DUPLICATE_MD: 'var(--rr-chart-purple, #8b5cf6)',
	ANOMALY_MD: 'var(--rr-chart-orange, #f97316)',
	RUN: 'var(--rr-chart-green, #22c55e)',
	WAVE: 'var(--rr-chart-red, #ef4444)',
};
