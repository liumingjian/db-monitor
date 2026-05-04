import type { AlertRuleResponse } from "@db-monitor/api-client";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	formatTimestamp,
} from "@db-monitor/ui";

export interface RuleAuditCopy {
	readonly heading: string;
	readonly description: string;
	readonly created: string;
	readonly placeholderEntry: string;
}

interface AuditEntry {
	readonly id: string;
	readonly timestamp: string;
	readonly title: string;
	readonly detail: string | null;
}

interface RuleAuditTimelineProps {
	readonly rule: AlertRuleResponse;
	readonly copy: RuleAuditCopy;
}

export function RuleAuditTimeline({ rule, copy }: RuleAuditTimelineProps) {
	const entries = buildTimeline(rule, copy);

	return (
		<Card>
			<CardHeader>
				<CardTitle>{copy.heading}</CardTitle>
				<CardDescription>{copy.description}</CardDescription>
			</CardHeader>
			<CardContent>
				<ol className="relative space-y-4 border-l border-border-hairline pl-4">
					{entries.map((entry) => (
						<li className="relative" key={entry.id}>
							<span className="absolute -left-[21px] top-1 h-3 w-3 rounded-full bg-accent" />
							<p className="text-xs font-mono tabular-nums text-fg-muted">
								{formatTimestamp(entry.timestamp)}
							</p>
							<p className="mt-1 text-sm font-medium text-fg-primary">{entry.title}</p>
							{entry.detail === null ? null : (
								<p className="mt-1 text-xs text-fg-muted">{entry.detail}</p>
							)}
						</li>
					))}
				</ol>
			</CardContent>
		</Card>
	);
}

function buildTimeline(rule: AlertRuleResponse, copy: RuleAuditCopy): readonly AuditEntry[] {
	return [
		{
			detail: null,
			id: `created-${rule.rule_id}`,
			timestamp: rule.created_at,
			title: copy.created,
		},
		{
			detail: null,
			id: `placeholder-${rule.rule_id}`,
			timestamp: rule.created_at,
			title: copy.placeholderEntry,
		},
	];
}
