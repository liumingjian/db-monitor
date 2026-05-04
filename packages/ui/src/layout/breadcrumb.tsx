import { ChevronRight as ChevronRightIcon } from "lucide-react";
import Link from "next/link";
import { Fragment } from "react";
import type { BreadcrumbItem } from "./types";
import { cn } from "./utils";

export interface BreadcrumbProps {
	readonly items: readonly BreadcrumbItem[];
	readonly className?: string;
}

/**
 * Inline breadcrumb for the top bar. The last item is rendered as the current
 * page (no link, fg-primary). Earlier items are links when `href` is set.
 */
export function Breadcrumb(props: BreadcrumbProps) {
	const { items, className } = props;
	if (items.length === 0) {
		return null;
	}

	return (
		<nav aria-label="Breadcrumb" className={cn("flex min-w-0 items-center text-sm", className)}>
			<ol className="flex min-w-0 items-center gap-1">
				{items.map((item, index) => {
					const isLast = index === items.length - 1;
					return (
						<Fragment key={`${item.label}-${index}`}>
							<li className="min-w-0 truncate">
								{isLast || !item.href ? (
									<span
										className={cn("truncate", isLast ? "text-fg-primary" : "text-fg-muted")}
										aria-current={isLast ? "page" : undefined}
									>
										{item.label}
									</span>
								) : (
									<Link
										href={item.href}
										className="truncate text-fg-muted transition-colors hover:text-fg-primary"
									>
										{item.label}
									</Link>
								)}
							</li>
							{!isLast ? (
								<li aria-hidden="true" className="text-fg-disabled">
									<ChevronRightIcon className="h-3.5 w-3.5" />
								</li>
							) : null}
						</Fragment>
					);
				})}
			</ol>
		</nav>
	);
}
