"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { IconRailItem } from "./icon-rail-item";
import type { IconRailGroup, IconRailGroupId } from "./types";

export interface IconRailProps {
	readonly groups: readonly IconRailGroup[];
	/** Bottom slot: typically user avatar + theme toggle. */
	readonly footer?: ReactNode;
}

/**
 * Pick the group whose `matchPrefixes` yields the longest prefix match against
 * the current pathname. Returns `null` if nothing matches.
 */
function resolveActiveGroup(
	groups: readonly IconRailGroup[],
	pathname: string,
): IconRailGroupId | null {
	let best: { id: IconRailGroupId; length: number } | null = null;

	for (const group of groups) {
		for (const prefix of group.matchPrefixes) {
			if (pathname === prefix || pathname.startsWith(`${prefix}/`)) {
				if (!best || prefix.length > best.length) {
					best = { id: group.id, length: prefix.length };
				}
			}
		}
	}

	return best?.id ?? null;
}

export function IconRail(props: IconRailProps) {
	const { groups, footer } = props;
	const pathname = usePathname() ?? "";
	const activeId = resolveActiveGroup(groups, pathname);

	return (
		<div className="flex h-full flex-col">
			<nav aria-label="Primary" className="flex flex-1 flex-col gap-1 py-3">
				{groups.map((group) => (
					<IconRailItem
						key={group.id}
						href={group.href}
						label={group.label}
						icon={group.icon}
						active={activeId === group.id}
					/>
				))}
			</nav>
			{footer ? (
				<div className="flex flex-col items-center gap-2 border-t border-border-hairline py-3">
					{footer}
				</div>
			) : null}
		</div>
	);
}
