import type { AlertRuleResponse } from "@db-monitor/api-client";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	EntityBadge,
	formatTimestamp,
} from "@db-monitor/ui";

import { formatScopeSummary } from "./rule-list-models";

export interface RuleDefinitionCopy {
	readonly heading: string;
	readonly description: string;
	readonly metaScope: string;
	readonly metaCreated: string;
	readonly metaEnabled: string;
	readonly metaDefaultThreshold: string;
	readonly metaOperator: string;
	readonly metaSeverity: string;
	readonly metaOverridesCount: string;
	readonly enabledOn: string;
	readonly enabledOff: string;
}

interface RuleDefinitionPanelProps {
	readonly rule: AlertRuleResponse;
	readonly copy: RuleDefinitionCopy;
}

export function RuleDefinitionPanel({ rule, copy }: RuleDefinitionPanelProps) {
	const rows: readonly { readonly title: string; readonly value: string }[] = [
		{ title: copy.metaScope, value: formatScopeSummary(rule) },
		{ title: copy.metaDefaultThreshold, value: String(rule.threshold) },
		{ title: copy.metaOperator, value: rule.operator },
		{ title: copy.metaSeverity, value: rule.severity },
		{ title: copy.metaEnabled, value: rule.enabled ? copy.enabledOn : copy.enabledOff },
		{ title: copy.metaOverridesCount, value: String(rule.overrides.length) },
		{ title: copy.metaCreated, value: formatTimestamp(rule.created_at) },
	];

	return (
		<Card>
			<CardHeader>
				<CardTitle>{copy.heading}</CardTitle>
				<CardDescription>{copy.description}</CardDescription>
			</CardHeader>
			<CardContent>
				<div className="flex flex-wrap gap-2">
					<EntityBadge
						label={rule.severity}
						tone={rule.severity === "critical" ? "critical" : "warning"}
					/>
					<EntityBadge label={rule.engine.toUpperCase()} tone="info" />
				</div>
				<dl className="mt-4 grid gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
					{rows.map((row) => (
						<div className="flex flex-col gap-1" key={row.title}>
							<dt className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
								{row.title}
							</dt>
							<dd className="font-mono tabular-nums text-fg-primary">{row.value}</dd>
						</div>
					))}
				</dl>
				<p className="mt-4 font-mono text-xs text-fg-muted">metric: {rule.metric_name}</p>
			</CardContent>
		</Card>
	);
}
