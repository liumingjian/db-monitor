"use client";

import type { NotifyHistoryResponse } from "@db-monitor/api-client";
import {
	Button,
	Dialog,
	DialogContent,
	DialogHeader,
	DialogTitle,
	EntityBadge,
	formatRelativeTime,
} from "@db-monitor/ui";
import { X as XIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

import { deriveAttemptsTimeline, matchesRow, toStatusKey, toStatusTone } from "./notify-view-model";

const DASH = "—";

export interface NotifyDrawerProps {
	readonly activeRowKey: string | null;
	readonly entries: readonly NotifyHistoryResponse[];
}

export function NotifyDrawer({ activeRowKey, entries }: NotifyDrawerProps) {
	const t = useTranslations("notifyHistory");
	const router = useRouter();
	const pathname = usePathname();
	const rawSearchParams = useSearchParams();

	const focus: NotifyHistoryResponse | null = activeRowKey
		? (entries.find((entry) => matchesRow(entry, activeRowKey)) ?? null)
		: null;

	const handleClose = useCallback(() => {
		const next = new URLSearchParams(rawSearchParams?.toString() ?? "");
		next.delete("row");
		const query = next.toString();
		router.replace(query.length === 0 ? pathname : `${pathname}?${query}`, { scroll: false });
	}, [pathname, rawSearchParams, router]);

	const handleOpenChange = useCallback(
		(next: boolean) => {
			if (!next) {
				handleClose();
			}
		},
		[handleClose],
	);

	if (focus === null) {
		return null;
	}

	const timeline = deriveAttemptsTimeline(entries, focus);

	return (
		<Dialog onOpenChange={handleOpenChange} open={true}>
			<DialogContent className="ml-auto mr-0 mt-0 h-dvh max-w-xl rounded-none rounded-l-lg border-l border-border-subtle">
				<DialogHeader className="flex flex-row items-start justify-between gap-4">
					<div className="min-w-0">
						<DialogTitle>{t("drawerTitle")}</DialogTitle>
						<p className="mt-1 truncate font-mono text-xs text-fg-muted" title={focus.rule_id}>
							{focus.rule_id}
						</p>
					</div>
					<Button
						aria-label={t("drawerClose")}
						onClick={handleClose}
						size="icon"
						type="button"
						variant="ghost"
					>
						<XIcon aria-hidden="true" className="h-4 w-4" />
					</Button>
				</DialogHeader>
				<div className="flex-1 overflow-y-auto">
					<SummarySection focus={focus} />
					<RecipientSection focus={focus} />
					<PayloadSection focus={focus} />
					<TimelineSection timeline={timeline} />
					<RelatedAlertSection focus={focus} />
					<ActionsSection />
				</div>
			</DialogContent>
		</Dialog>
	);
}

interface FocusProps {
	readonly focus: NotifyHistoryResponse;
}

function DrawerSection({ children, title }: { children: React.ReactNode; title: string }) {
	return (
		<section className="border-b border-border-hairline px-5 py-4 last:border-b-0">
			<h3 className="text-[11px] font-semibold uppercase tracking-widest text-fg-muted">{title}</h3>
			<div className="mt-3 flex flex-col gap-2 text-sm text-fg-primary">{children}</div>
		</section>
	);
}

function KeyValueRow({ label, value }: { label: string; value: React.ReactNode }) {
	return (
		<div className="flex items-start justify-between gap-4">
			<span className="text-fg-muted">{label}</span>
			<span className="min-w-0 flex-1 text-right">{value}</span>
		</div>
	);
}

function SummarySection({ focus }: FocusProps) {
	const t = useTranslations("notifyHistory");
	const statusKey = toStatusKey(focus.status);
	const label = t(`status${statusKey.charAt(0).toUpperCase()}${statusKey.slice(1)}`);
	return (
		<DrawerSection title={t("sectionSummary")}>
			<KeyValueRow
				label={t("summaryChannel")}
				value={<span className="font-mono">{focus.channel}</span>}
			/>
			<KeyValueRow
				label={t("summaryStatus")}
				value={<EntityBadge label={label} tone={toStatusTone(focus.status)} />}
			/>
			<KeyValueRow
				label={t("summaryAttempt")}
				value={<span className="font-mono tabular-nums">#{focus.attempt}</span>}
			/>
			<KeyValueRow
				label={t("summaryAttemptedAt")}
				value={<TimestampDisplay iso={focus.attempted_at} />}
			/>
			<KeyValueRow
				label={t("summaryDeliveredAt")}
				value={
					focus.delivered_at ? (
						<TimestampDisplay iso={focus.delivered_at} />
					) : (
						<span className="font-mono text-fg-muted">{DASH}</span>
					)
				}
			/>
			<KeyValueRow
				label={t("summaryOrganization")}
				value={<span className="font-mono text-xs">{focus.organization_id}</span>}
			/>
		</DrawerSection>
	);
}

function RecipientSection({ focus }: FocusProps) {
	const t = useTranslations("notifyHistory");
	return (
		<DrawerSection title={t("sectionRecipient")}>
			<KeyValueRow
				label={t("recipientRule")}
				value={<span className="font-mono">{focus.rule_id}</span>}
			/>
			<KeyValueRow
				label={t("recipientInstance")}
				value={
					focus.instance_id ? (
						<span className="font-mono">{focus.instance_id}</span>
					) : (
						<span className="text-fg-muted">{t("recipientFleetWide")}</span>
					)
				}
			/>
			<KeyValueRow
				label={t("recipientChannelBinding")}
				value={
					<Link className="text-accent hover:underline" href="/admin/channels">
						{t("recipientBindingHint")}
					</Link>
				}
			/>
		</DrawerSection>
	);
}

function PayloadSection({ focus }: FocusProps) {
	const t = useTranslations("notifyHistory");
	return (
		<DrawerSection title={t("sectionPayload")}>
			<p className="text-xs text-fg-muted">{t("payloadHint")}</p>
			<KeyValueRow
				label={t("payloadChannelField")}
				value={<span className="font-mono">{focus.channel}</span>}
			/>
			<KeyValueRow
				label={t("payloadErrorField")}
				value={
					focus.error ? (
						<span className="font-mono text-xs text-sev-critical">{focus.error}</span>
					) : (
						<span className="text-fg-muted">{t("payloadNoError")}</span>
					)
				}
			/>
		</DrawerSection>
	);
}

function TimelineSection({ timeline }: { timeline: readonly NotifyHistoryResponse[] }) {
	const t = useTranslations("notifyHistory");
	if (timeline.length === 0) {
		return (
			<DrawerSection title={t("sectionAttemptsTimeline")}>
				<p className="text-sm text-fg-muted">{t("timelineEmpty")}</p>
			</DrawerSection>
		);
	}
	return (
		<DrawerSection title={t("sectionAttemptsTimeline")}>
			<ol className="flex flex-col gap-3">
				{timeline.map((entry) => (
					<TimelineItem
						attempt={entry.attempt}
						attemptedAt={entry.attempted_at}
						error={entry.error}
						key={`${entry.attempt}|${entry.attempted_at}`}
						status={entry.status}
					/>
				))}
			</ol>
			<p className="text-[11px] text-fg-muted">{t("timelineAggregatedFromPage")}</p>
		</DrawerSection>
	);
}

interface TimelineItemProps {
	readonly attempt: number;
	readonly attemptedAt: string;
	readonly error: string | null;
	readonly status: string;
}

function TimelineItem({ attempt, attemptedAt, error, status }: TimelineItemProps) {
	const t = useTranslations("notifyHistory");
	const statusKey = toStatusKey(status);
	const label = t(`status${statusKey.charAt(0).toUpperCase()}${statusKey.slice(1)}`);
	return (
		<li className="rounded-md border border-border-hairline bg-bg-elevated p-3">
			<div className="flex items-center justify-between gap-2">
				<span className="text-xs font-medium text-fg-primary">
					{t("timelineAttempt", { attempt })}
				</span>
				<EntityBadge label={label} tone={toStatusTone(status)} />
			</div>
			<div className="mt-1 font-mono text-xs text-fg-muted">
				<TimestampDisplay iso={attemptedAt} />
			</div>
			{error ? <p className="mt-2 break-all font-mono text-xs text-sev-critical">{error}</p> : null}
		</li>
	);
}

function RelatedAlertSection({ focus }: FocusProps) {
	const t = useTranslations("notifyHistory");
	const alertHref =
		focus.instance_id === null
			? "/alerts"
			: `/alerts?instance=${encodeURIComponent(focus.instance_id)}`;
	return (
		<DrawerSection title={t("sectionRelatedAlert")}>
			<div className="flex flex-wrap gap-2">
				<Button asChild size="sm" variant="outline">
					<Link href={`/rules/${encodeURIComponent(focus.rule_id)}`}>{t("relatedRule")}</Link>
				</Button>
				{focus.instance_id ? (
					<Button asChild size="sm" variant="outline">
						<Link href={`/instances/${encodeURIComponent(focus.instance_id)}`}>
							{t("relatedInstance")}
						</Link>
					</Button>
				) : null}
				<Button asChild size="sm" variant="outline">
					<Link href={alertHref}>{t("relatedAlertQueue")}</Link>
				</Button>
			</div>
		</DrawerSection>
	);
}

function ActionsSection() {
	const t = useTranslations("notifyHistory");
	return (
		<DrawerSection title={t("sectionActions")}>
			<ActionsPlaceholder title={t("actionsRetryTitle")} hint={t("actionsRetryHint")} />
			<ActionsPlaceholder title={t("actionsMuteTitle")} hint={t("actionsMuteHint")} />
		</DrawerSection>
	);
}

function ActionsPlaceholder({ hint, title }: { hint: string; title: string }) {
	return (
		<div className="rounded-md border border-dashed border-border-subtle bg-bg-base p-3">
			<p className="text-sm font-medium text-fg-secondary">{title}</p>
			<p className="mt-1 text-xs text-fg-muted">{hint}</p>
		</div>
	);
}

function TimestampDisplay({ iso }: { iso: string }) {
	return (
		<span className="font-mono tabular-nums" title={iso}>
			{formatRelativeTime(iso)}
		</span>
	);
}
