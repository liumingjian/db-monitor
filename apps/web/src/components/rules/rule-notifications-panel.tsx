import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@db-monitor/ui";

export interface RuleNotificationsCopy {
	readonly heading: string;
	readonly description: string;
	readonly placeholder: string;
	readonly emptyChannels: string;
}

interface RuleNotificationsPanelProps {
	readonly copy: RuleNotificationsCopy;
}

export function RuleNotificationsPanel({ copy }: RuleNotificationsPanelProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>{copy.heading}</CardTitle>
				<CardDescription>{copy.description}</CardDescription>
			</CardHeader>
			<CardContent>
				<div className="rounded-md border border-dashed border-border-hairline px-4 py-6 text-sm text-fg-muted">
					{copy.emptyChannels}
				</div>
				<p className="mt-3 text-xs text-fg-muted">{copy.placeholder}</p>
			</CardContent>
		</Card>
	);
}
