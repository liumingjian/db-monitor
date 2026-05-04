"use client";

import { EntityBadge } from "@db-monitor/ui";
import { useTranslations } from "next-intl";

import { toStatusKey, toStatusTone } from "./notify-view-model";

export interface NotifyStatusBadgeProps {
	readonly status: string;
}

/**
 * Severity-tone badge for a notifier delivery status. Uses the ADR-0012
 * four-color severity axis and next-intl for labels.
 */
export function NotifyStatusBadge({ status }: NotifyStatusBadgeProps) {
	const t = useTranslations("notifyHistory");
	const tone = toStatusTone(status);
	const key = toStatusKey(status);
	const labelKey = `status${key.charAt(0).toUpperCase()}${key.slice(1)}`;
	return <EntityBadge tone={tone} label={t(labelKey)} />;
}
