"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";

export interface NotifyLoadMoreProps {
	readonly nextHref: string;
}

/**
 * "Load more" link to the next Feed page. Implemented as a link (not a button)
 * so it round-trips through the URL and remains bookmarkable; the server reruns
 * `listNotifyHistory` with the elevated `limit`.
 */
export function NotifyLoadMore({ nextHref }: NotifyLoadMoreProps) {
	const t = useTranslations("notifyHistory");
	return (
		<div className="flex flex-col items-center gap-1 py-3">
			<Link
				className="inline-flex h-8 items-center rounded-md border border-border-subtle bg-bg-elevated px-4 text-xs font-medium text-fg-primary transition-colors hover:bg-surface-overlay"
				href={nextHref}
				scroll={false}
			>
				{t("loadMore")}
			</Link>
			<p className="text-[11px] text-fg-muted">{t("loadMoreHint")}</p>
		</div>
	);
}
