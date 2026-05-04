import type { ReactNode } from "react";
import { cn } from "./utils";

export interface PageContentProps {
	readonly children: ReactNode;
	readonly className?: string;
}

/**
 * Main scrollable content region inside the canonical page template.
 * Fills remaining height; 24px horizontal + vertical padding.
 */
export function PageContent(props: PageContentProps) {
	const { children, className } = props;

	return (
		<div className={cn("flex min-h-0 flex-1 flex-col gap-6 overflow-auto p-6", className)}>
			{children}
		</div>
	);
}
