import type { ReactNode } from "react";
import { EntityBadge } from "./entity-badge";
import type { EntityBadgeModel } from "./types";
import { cn } from "./utils";

export interface EntitySummaryProps {
	readonly avatar?: ReactNode;
	readonly title: string;
	readonly subtitle?: string;
	readonly badges?: readonly EntityBadgeModel[];
	readonly actions?: ReactNode;
	readonly className?: string;
}

/**
 * 88px entity summary row: optional avatar, title + subtitle + badge stack,
 * right-aligned actions slot.
 */
export function EntitySummary(props: EntitySummaryProps) {
	const { avatar, title, subtitle, badges, actions, className } = props;

	return (
		<div
			className={cn(
				"flex h-[88px] shrink-0 items-center gap-4 border-b border-border-hairline px-6",
				className,
			)}
		>
			{avatar ? <div className="shrink-0">{avatar}</div> : null}
			<div className="flex min-w-0 flex-1 flex-col gap-1">
				<div className="flex min-w-0 items-center gap-2">
					<h1 className="truncate text-lg font-semibold text-fg-primary">{title}</h1>
					{badges && badges.length > 0 ? (
						<div className="flex flex-wrap items-center gap-1.5">
							{badges.map((badge, index) => (
								<EntityBadge
									key={`${badge.tone}-${badge.label}-${index}`}
									tone={badge.tone}
									label={badge.label}
								/>
							))}
						</div>
					) : null}
				</div>
				{subtitle ? <p className="truncate text-sm text-fg-muted">{subtitle}</p> : null}
			</div>
			{actions ? <div className="flex shrink-0 items-center gap-2">{actions}</div> : null}
		</div>
	);
}
