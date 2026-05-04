import type { ReactNode } from "react";
import { cn } from "./utils";

export interface AppShellProps {
	readonly iconRail: ReactNode;
	readonly sidebar: ReactNode;
	readonly topBar: ReactNode;
	readonly children: ReactNode;
	readonly className?: string;
}

/**
 * Top-level application shell.
 *
 * Layout:
 *   col 1 = 64px icon rail
 *   col 2 = 216px contextual sidebar
 *   col 3 = flex main (top bar 56px + content)
 */
export function AppShell(props: AppShellProps) {
	const { iconRail, sidebar, topBar, children, className } = props;

	return (
		<div
			className={cn(
				"flex h-dvh w-full bg-bg-deep text-fg-primary",
				"font-sans antialiased",
				className,
			)}
		>
			<aside className="flex w-16 shrink-0 flex-col border-r border-border-hairline bg-bg-base">
				{iconRail}
			</aside>
			<aside className="flex w-[216px] shrink-0 flex-col border-r border-border-hairline bg-bg-base">
				{sidebar}
			</aside>
			<div className="flex min-w-0 flex-1 flex-col">
				<header className="flex h-14 shrink-0 items-center border-b border-border-hairline bg-bg-base">
					{topBar}
				</header>
				<main className="min-h-0 flex-1 overflow-auto bg-bg-deep">{children}</main>
			</div>
		</div>
	);
}
