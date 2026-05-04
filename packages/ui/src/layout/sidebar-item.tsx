"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { SidebarItemModel } from "./types";
import { cn } from "./utils";

export interface SidebarItemProps {
	readonly item: SidebarItemModel;
	readonly depth?: number;
}

function isHrefActive(pathname: string, href: string): boolean {
	if (pathname === href) {
		return true;
	}
	return pathname.startsWith(`${href}/`);
}

export function SidebarItem(props: SidebarItemProps) {
	const { item, depth = 0 } = props;
	const pathname = usePathname() ?? "";
	const active = isHrefActive(pathname, item.href);
	const Icon = item.icon;

	// Flatten to 2 levels max per spec (children rendered, grandchildren ignored).
	const showChildren = depth === 0 && item.children && item.children.length > 0;

	return (
		<div className="flex flex-col">
			<Link
				href={item.href}
				aria-current={active ? "page" : undefined}
				className={cn(
					"flex h-9 items-center gap-2 rounded-md px-2 text-sm",
					"transition-colors duration-150 ease-out",
					"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
					depth === 0 ? "" : "ml-4",
					active
						? "bg-accent/10 text-accent"
						: "text-fg-secondary hover:bg-surface-overlay hover:text-fg-primary",
				)}
			>
				{Icon ? <Icon className="h-4 w-4 shrink-0" aria-hidden="true" /> : null}
				<span className="flex-1 truncate">{item.label}</span>
				{item.badge !== undefined ? (
					<span
						className={cn(
							"inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5",
							"text-[11px] font-medium",
							active ? "bg-accent text-on-accent" : "bg-surface-overlay text-fg-muted",
						)}
					>
						{item.badge}
					</span>
				) : null}
			</Link>
			{showChildren ? (
				<div className="mt-0.5 flex flex-col gap-0.5">
					{item.children?.map((child) => (
						<SidebarItem key={child.href} item={child} depth={depth + 1} />
					))}
				</div>
			) : null}
		</div>
	);
}
