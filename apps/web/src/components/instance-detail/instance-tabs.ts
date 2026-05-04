import type { DatabaseEngine } from "@db-monitor/api-client";
import type { TabItem } from "@db-monitor/ui";

export type InstanceTabKey =
	| "overview"
	| "performance"
	| "sessions"
	| "sql"
	| "storage"
	| "replication"
	| "configuration"
	| "audit";

export interface InstanceTabDescriptor {
	readonly key: InstanceTabKey;
	readonly href: string;
	readonly label: string;
	readonly segment: string;
	/**
	 * `strong` = engine natively supports this tab (live data).
	 * `weak` = tab still visible for navigation symmetry but content is an
	 *   engine-unsupported notice (e.g. MySQL opening "存储").
	 * `placeholder` = Tier 3 honest placeholder for Slice 2 feature.
	 */
	readonly capability: "strong" | "weak" | "placeholder";
}

interface BuildInstanceTabsInput {
	readonly instanceId: string;
	readonly engine: DatabaseEngine;
}

/**
 * Q13 规则 1：8 tab 固定顺序；engine 差异反映在 capability 字段（而非隐藏 tab），
 * 避免 URL 深链失效。
 */
export function buildInstanceTabs(input: BuildInstanceTabsInput): readonly InstanceTabDescriptor[] {
	const base = `/instances/${input.instanceId}`;
	return [
		{
			capability: "strong",
			href: base,
			key: "overview",
			label: "概览",
			segment: "overview",
		},
		{
			capability: "strong",
			href: `${base}/performance`,
			key: "performance",
			label: "性能",
			segment: "performance",
		},
		{
			capability: "strong",
			href: `${base}/processes`,
			key: "sessions",
			label: "会话",
			segment: "processes",
		},
		{
			capability: input.engine === "mysql" ? "strong" : "weak",
			href: `${base}/slow-queries`,
			key: "sql",
			label: "SQL",
			segment: "slow-queries",
		},
		{
			capability: input.engine === "oracle" ? "strong" : "weak",
			href: `${base}/tablespaces`,
			key: "storage",
			label: "存储",
			segment: "tablespaces",
		},
		{
			capability: "placeholder",
			href: `${base}/replication`,
			key: "replication",
			label: "复制",
			segment: "replication",
		},
		{
			capability: "placeholder",
			href: `${base}/configuration`,
			key: "configuration",
			label: "配置",
			segment: "configuration",
		},
		{
			capability: "strong",
			href: `${base}/audit`,
			key: "audit",
			label: "审计",
			segment: "audit",
		},
	];
}

export function toTabItems(tabs: readonly InstanceTabDescriptor[]): readonly TabItem[] {
	return tabs.map((tab) => ({
		href: tab.href,
		key: tab.key,
		label: tab.label,
	}));
}
