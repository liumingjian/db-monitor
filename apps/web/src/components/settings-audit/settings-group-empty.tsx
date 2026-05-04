import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@db-monitor/ui";

export interface SettingsGroupEmptyProps {
	readonly title: string;
	readonly hint: string;
}

export function SettingsGroupEmpty(props: SettingsGroupEmptyProps) {
	const { title, hint } = props;
	return (
		<Card className="border-dashed">
			<CardHeader>
				<CardTitle>{title}</CardTitle>
				<CardDescription>{hint}</CardDescription>
			</CardHeader>
			<CardContent>
				<div className="flex h-24 items-center justify-center rounded-md border border-dashed border-border-hairline text-sm text-fg-muted">
					—
				</div>
			</CardContent>
		</Card>
	);
}
