"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export interface InstanceTabDescriptor {
	readonly href: string;
	readonly label: string;
	readonly segment: "overview" | "processes" | "slow-queries" | "tablespaces";
}

interface InstanceTabNavProps {
	readonly tabs: readonly InstanceTabDescriptor[];
}

export function InstanceTabNav({ tabs }: InstanceTabNavProps) {
	const pathname = usePathname() ?? "";
	return (
		<nav aria-label="Instance sections" className="flex flex-wrap gap-2">
			{tabs.map((tab) => (
				<Link
					aria-current={isActive(pathname, tab) ? "page" : undefined}
					className={tabClassName(isActive(pathname, tab))}
					href={tab.href}
					key={tab.segment}
				>
					{tab.label}
				</Link>
			))}
		</nav>
	);
}

function isActive(pathname: string, tab: InstanceTabDescriptor): boolean {
	if (tab.segment === "overview") {
		return pathname === tab.href;
	}
	return pathname === tab.href || pathname.startsWith(`${tab.href}/`);
}

function tabClassName(active: boolean): string {
	if (active) {
		return "rounded-full bg-[var(--accent)] px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-white";
	}
	return "rounded-full border border-black/10 bg-white px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)] transition hover:border-[var(--accent)] hover:text-[var(--ink)]";
}
