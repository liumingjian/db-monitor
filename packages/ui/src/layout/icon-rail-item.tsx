"use client";

import Link from "next/link";
import type { IconComponent } from "./types";
import { cn } from "./utils";

export interface IconRailItemProps {
	readonly href: string;
	readonly label: string;
	readonly icon: IconComponent;
	readonly active?: boolean;
}

/**
 * Single icon on the 64px rail.
 * Shows a 3px cyan active indicator on the left edge when active.
 */
export function IconRailItem(props: IconRailItemProps) {
	const { href, label, icon: Icon, active = false } = props;

	return (
		<Link
			href={href}
			aria-label={label}
			aria-current={active ? "page" : undefined}
			title={label}
			className={cn(
				"group relative flex h-12 w-full items-center justify-center",
				"transition-colors duration-150 ease-out",
				"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
				active ? "text-fg-primary" : "text-fg-muted hover:text-fg-primary hover:bg-surface-overlay",
			)}
		>
			<span
				aria-hidden="true"
				className={cn(
					"absolute left-0 top-1/2 h-8 w-[3px] -translate-y-1/2 rounded-r bg-accent",
					"transition-opacity duration-150",
					active ? "opacity-100" : "opacity-0",
				)}
			/>
			<Icon className="h-5 w-5" aria-hidden="true" />
		</Link>
	);
}
