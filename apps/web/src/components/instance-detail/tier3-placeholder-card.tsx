import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@db-monitor/ui";

export interface Tier3PlaceholderCardProps {
	readonly title: string;
	readonly statusLabel: string;
	readonly description: string;
	readonly capabilities: readonly string[];
}

/**
 * Tier 3 honest placeholder：标注交付状态与预计能力。
 * 不伪造数据、不挂后端未落地的端点。
 */
export function Tier3PlaceholderCard(props: Tier3PlaceholderCardProps) {
	return (
		<div className="px-6 py-6">
			<Card className="max-w-2xl">
				<CardHeader>
					<div className="flex items-center gap-2">
						<CardTitle>{props.title}</CardTitle>
						<span className="inline-flex items-center rounded-md border border-border-subtle bg-surface-overlay px-2 py-0.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-fg-muted">
							{props.statusLabel}
						</span>
					</div>
					<CardDescription>{props.description}</CardDescription>
				</CardHeader>
				<CardContent>
					<ul className="ml-5 list-disc space-y-1.5 text-sm text-fg-secondary">
						{props.capabilities.map((capability) => (
							<li key={capability}>{capability}</li>
						))}
					</ul>
				</CardContent>
			</Card>
		</div>
	);
}
