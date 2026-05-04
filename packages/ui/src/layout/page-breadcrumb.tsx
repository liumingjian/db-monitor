import { Breadcrumb } from "./breadcrumb";
import type { BreadcrumbItem } from "./types";
import { cn } from "./utils";

export interface PageBreadcrumbProps {
	readonly items: readonly BreadcrumbItem[];
	readonly className?: string;
}

/**
 * 40px breadcrumb slot sitting at the top of the canonical page template.
 */
export function PageBreadcrumb(props: PageBreadcrumbProps) {
	const { items, className } = props;

	return (
		<div
			className={cn(
				"flex h-10 shrink-0 items-center border-b border-border-hairline px-6",
				className,
			)}
		>
			<Breadcrumb items={items} />
		</div>
	);
}
