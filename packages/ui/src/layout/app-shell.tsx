import type { ReactNode } from "react";
import { SidebarMobileProvider } from "./sidebar-mobile";
import { cn } from "./utils";

export type AppShellChrome = "full" | "screen";

export interface AppShellProps {
	readonly sidebar?: ReactNode;
	readonly topBar: ReactNode;
	readonly children: ReactNode;
	readonly chrome?: AppShellChrome;
	readonly className?: string;
}

/**
 * Top-level application shell.
 *
 * `chrome="full"` (default): renders sidebar + top bar + content.
 * `chrome="screen"`: hides sidebar (Slice 3 dashboards). Top bar still rendered;
 *   pass `null` from the page if a fully chrome-less layout is needed.
 *
 * The shell is responsive:
 * - At md+ the sidebar is rendered inline (flex-row).
 * - Below md the sidebar collapses into a drawer; trigger via
 *   `<SidebarMenuButton />` placed inside the top bar.
 */
export function AppShell(props: AppShellProps) {
	const { sidebar, topBar, children, chrome = "full", className } = props;
	const showSidebar = chrome === "full" && sidebar !== undefined;

	return (
		<SidebarMobileProvider>
			<div
				className={cn(
					"flex h-dvh w-full bg-bg-deep text-fg-primary",
					"font-sans antialiased",
					className,
				)}
			>
				{showSidebar ? sidebar : null}
				<div className="flex min-w-0 flex-1 flex-col">
					<header className="flex h-14 shrink-0 items-center border-b border-border-hairline bg-bg-base">
						{topBar}
					</header>
					<main className="min-h-0 flex-1 overflow-auto bg-bg-deep">{children}</main>
				</div>
			</div>
		</SidebarMobileProvider>
	);
}
