import type { ReactNode } from "react";
import { SidebarItem } from "./sidebar-item";
import type { IconRailGroupId, SidebarItemModel } from "./types";

export interface ContextualSidebarProps {
	readonly activeGroup: IconRailGroupId;
	readonly groupLabel: string;
	readonly groupBadge?: ReactNode;
	readonly items: readonly SidebarItemModel[];
	readonly footer?: ReactNode;
}

/**
 * 216px secondary navigation panel. Header is 48px, followed by a scrolling
 * item list. `activeGroup` is kept in the API so consumers can gate rendering
 * via React keys (re-mount on group change).
 */
export function ContextualSidebar(props: ContextualSidebarProps) {
	const { activeGroup, groupLabel, groupBadge, items, footer } = props;

	return (
		<div className="flex h-full flex-col" data-group={activeGroup}>
			<div className="flex h-12 shrink-0 items-center justify-between border-b border-border-hairline px-3">
				<span className="text-[11px] font-medium uppercase tracking-widest text-fg-muted">
					{groupLabel}
				</span>
				{groupBadge}
			</div>
			<nav aria-label={groupLabel} className="flex-1 overflow-y-auto px-2 py-3">
				<ul className="flex flex-col gap-0.5">
					{items.map((item) => (
						<li key={item.href}>
							<SidebarItem item={item} />
						</li>
					))}
				</ul>
			</nav>
			{footer ? <div className="border-t border-border-hairline px-3 py-2">{footer}</div> : null}
		</div>
	);
}
