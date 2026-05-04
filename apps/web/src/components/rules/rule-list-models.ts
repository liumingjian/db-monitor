import type { AlertRuleResponse } from "@db-monitor/api-client";

export type EngineFilterValue = "" | "mysql" | "oracle";
export type SeverityFilterValue = "" | "warning" | "critical";
export type EnabledFilterValue = "" | "enabled" | "disabled";

export interface RulesCatalogFilters {
	readonly engine: EngineFilterValue;
	readonly severity: SeverityFilterValue;
	readonly enabled: EnabledFilterValue;
	readonly query: string;
}

export const EMPTY_RULES_FILTERS: RulesCatalogFilters = {
	engine: "",
	severity: "",
	enabled: "",
	query: "",
};

export function filterRules(
	rules: readonly AlertRuleResponse[],
	filters: RulesCatalogFilters,
): readonly AlertRuleResponse[] {
	const normalizedQuery = filters.query.trim().toLowerCase();
	return rules.filter((rule) => matchesFilters(rule, filters, normalizedQuery));
}

function matchesFilters(
	rule: AlertRuleResponse,
	filters: RulesCatalogFilters,
	normalizedQuery: string,
): boolean {
	if (filters.engine !== "" && rule.engine !== filters.engine) {
		return false;
	}
	if (filters.severity !== "" && rule.severity !== filters.severity) {
		return false;
	}
	if (filters.enabled === "enabled" && !rule.enabled) {
		return false;
	}
	if (filters.enabled === "disabled" && rule.enabled) {
		return false;
	}
	if (normalizedQuery.length === 0) {
		return true;
	}
	const haystack = `${rule.name} ${rule.metric_name}`.toLowerCase();
	return haystack.includes(normalizedQuery);
}

export function countOverrides(rule: AlertRuleResponse): number {
	return rule.overrides.length;
}

export function formatScopeSummary(rule: AlertRuleResponse): string {
	if (rule.instance_ids.length === 0) {
		return rule.engine === "oracle" ? "全部 Oracle 实例" : "全部 MySQL 实例";
	}
	if (rule.instance_ids.length <= 2) {
		return rule.instance_ids.join(", ");
	}
	const head = rule.instance_ids.slice(0, 2).join(", ");
	return `${head} +${rule.instance_ids.length - 2}`;
}
