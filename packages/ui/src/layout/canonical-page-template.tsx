import type { ReactNode } from "react";
import { cn } from "./utils";

export interface CanonicalPageTemplateProps {
	readonly children: ReactNode;
	readonly className?: string;
}

/**
 * Canonical 7-segment page template container.
 *
 * Expected (optional) children composition order:
 *   PageBreadcrumb -> EntitySummary -> QuickMetrics -> TabBar -> PageContent
 *
 * All segments are optional; consumers compose whichever slots apply.
 */
export function CanonicalPageTemplate(props: CanonicalPageTemplateProps) {
	const { children, className } = props;

	return (
		<section className={cn("flex h-full w-full flex-col bg-bg-deep text-fg-primary", className)}>
			{children}
		</section>
	);
}
