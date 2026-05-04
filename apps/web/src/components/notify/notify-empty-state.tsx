"use client";

import { useTranslations } from "next-intl";

export type NotifyEmptyVariant = "firstRun" | "filtered" | "busy";

export interface NotifyEmptyStateProps {
	readonly variant: NotifyEmptyVariant;
}

const TITLE_KEY: Record<NotifyEmptyVariant, string> = {
	busy: "emptyBusyTitle",
	filtered: "emptyFilteredTitle",
	firstRun: "emptyFirstRunTitle",
};

const HINT_KEY: Record<NotifyEmptyVariant, string> = {
	busy: "emptyBusyHint",
	filtered: "emptyFilteredHint",
	firstRun: "emptyFirstRunHint",
};

/**
 * Three-branch empty state per ADR-0012 D7 (first run / filtered / business empty).
 */
export function NotifyEmptyState({ variant }: NotifyEmptyStateProps) {
	const t = useTranslations("notifyHistory");
	return (
		<div className="rounded-md border border-dashed border-border-subtle bg-bg-elevated p-10 text-center">
			<p className="text-base font-medium text-fg-primary">{t(TITLE_KEY[variant])}</p>
			<p className="mt-2 text-sm text-fg-muted">{t(HINT_KEY[variant])}</p>
		</div>
	);
}
