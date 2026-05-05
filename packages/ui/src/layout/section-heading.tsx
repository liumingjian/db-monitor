import type { ReactNode } from "react";
import { cn } from "./utils";

export interface SectionHeadingProps {
	readonly label: string;
	readonly description?: string;
	readonly endSlot?: ReactNode;
	readonly className?: string;
	readonly as?: "h2" | "h3";
}

/**
 * Page-level section heading: 11px uppercase 0.10em label + optional descriptor +
 * optional end slot, with a hairline divider directly below. Replaces the
 * "panel-in-panel" wrapper for grouping content sections inside a page.
 *
 * PR β.1 Variant-A template (ADR-0012 D6/D7).
 */
export function SectionHeading(props: SectionHeadingProps) {
	const { label, description, endSlot, className, as = "h2" } = props;
	const Heading = as;
	return (
		<div
			className={cn(
				"flex flex-wrap items-baseline gap-x-3 gap-y-1 border-b border-border-hairline pb-2",
				className,
			)}
		>
			<Heading className="text-[11px] font-semibold uppercase tracking-[0.10em] text-fg-muted">
				{label}
			</Heading>
			{description ? <span className="text-[11px] text-fg-muted">{description}</span> : null}
			{endSlot ? (
				<div className="ml-auto flex items-center gap-3 text-[11px] text-fg-muted">{endSlot}</div>
			) : null}
		</div>
	);
}
