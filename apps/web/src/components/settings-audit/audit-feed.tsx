"use client";

import {
	Badge,
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	cn,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { useState } from "react";

import { AuditDrawer } from "./audit-drawer";
import type { AuditEvent, AuditSeverity } from "./audit-event-model";

export interface AuditFeedProps {
	readonly events: readonly AuditEvent[];
	readonly limit: number;
	readonly currentUserId: string | null;
}

const SEVERITY_VARIANT: Record<AuditSeverity, "destructive" | "warning" | "info" | "ok"> = {
	critical: "destructive",
	warning: "warning",
	info: "info",
	ok: "ok",
};

export function AuditFeed(props: AuditFeedProps) {
	const { events, limit, currentUserId } = props;
	const t = useTranslations("audit");
	const [selectedId, setSelectedId] = useState<string | null>(null);

	const selectedEvent = events.find((event) => event.id === selectedId) ?? null;

	if (events.length === 0) {
		return (
			<Card>
				<CardHeader>
					<CardTitle>{t("feedEmpty")}</CardTitle>
					<CardDescription>{t("feedEmptyHint")}</CardDescription>
				</CardHeader>
			</Card>
		);
	}

	return (
		<>
			<Card>
				<CardHeader>
					<CardTitle>{t("feedHeading")}</CardTitle>
					<CardDescription>{t("feedHint", { limit })}</CardDescription>
				</CardHeader>
				<CardContent className="p-0">
					<div className="overflow-x-auto">
						<table className="w-full min-w-[920px] border-collapse text-left text-sm">
							<thead className="bg-bg-base text-xs uppercase tracking-wider text-fg-muted">
								<tr>
									<th className="px-4 py-2 font-medium">{t("feedColumnTime")}</th>
									<th className="px-4 py-2 font-medium">{t("feedColumnType")}</th>
									<th className="px-4 py-2 font-medium">{t("feedColumnSeverity")}</th>
									<th className="px-4 py-2 font-medium">{t("feedColumnActor")}</th>
									<th className="px-4 py-2 font-medium">{t("feedColumnTarget")}</th>
									<th className="px-4 py-2 font-medium" />
								</tr>
							</thead>
							<tbody>
								{events.map((event) => (
									<AuditRow
										key={event.id}
										event={event}
										currentUserId={currentUserId}
										onOpen={() => setSelectedId(event.id)}
									/>
								))}
							</tbody>
						</table>
					</div>
				</CardContent>
			</Card>
			<AuditDrawer
				event={selectedEvent}
				currentUserId={currentUserId}
				onClose={() => setSelectedId(null)}
			/>
		</>
	);
}

interface AuditRowProps {
	readonly event: AuditEvent;
	readonly currentUserId: string | null;
	readonly onOpen: () => void;
}

function AuditRow(props: AuditRowProps) {
	const { event, currentUserId, onOpen } = props;
	const t = useTranslations("audit");

	const actorLabel =
		event.actor.isSystem === true
			? t("drawerActorSystem")
			: (event.actor.displayName ?? event.actor.username ?? t("drawerActorUnknown"));

	const isSelf = event.actor.userId !== null && event.actor.userId === currentUserId;

	return (
		<tr className="border-t border-border-hairline align-top hover:bg-surface-overlay">
			<td className="px-4 py-3 font-mono text-xs tabular-nums text-fg-secondary">
				{event.occurredAt}
			</td>
			<td className="px-4 py-3">
				<span className="font-medium text-fg-primary">{t(eventI18nKey(event.type))}</span>
				<p className="font-mono text-[11px] text-fg-muted">{event.type}</p>
			</td>
			<td className="px-4 py-3">
				<Badge variant={SEVERITY_VARIANT[event.severity]} size="sm">
					{event.severity}
				</Badge>
			</td>
			<td className="px-4 py-3">
				<span className={cn("text-sm", isSelf && "font-semibold text-accent")}>{actorLabel}</span>
				{isSelf ? <p className="text-[11px] text-accent">{t("drawerActorSelf")}</p> : null}
			</td>
			<td className="px-4 py-3">
				<span className="text-sm text-fg-primary">{event.target.label}</span>
				<p className="font-mono text-[11px] text-fg-muted">
					{event.target.type} · {event.target.id}
				</p>
			</td>
			<td className="px-4 py-3 text-right">
				<Button variant="outline" size="sm" onClick={onOpen}>
					{t("feedViewDetails")}
				</Button>
			</td>
		</tr>
	);
}

function eventI18nKey(type: AuditEvent["type"]): string {
	switch (type) {
		case "alert.opened":
			return "eventAlertOpened";
		case "alert.acknowledged":
			return "eventAlertAcknowledged";
		case "alert.owner_assigned":
			return "eventAlertOwnerAssigned";
		case "alert.resolved":
			return "eventAlertResolved";
		case "setting.updated":
			return "eventSettingUpdated";
		case "notify.delivered":
			return "eventNotifyDelivered";
		case "notify.failed":
			return "eventNotifyFailed";
		case "notify.skipped":
			return "eventNotifySkipped";
	}
}
