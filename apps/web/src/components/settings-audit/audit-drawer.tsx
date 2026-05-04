"use client";

import {
	Badge,
	Button,
	Dialog,
	DialogBody,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";

import type { AuditEvent } from "./audit-event-model";

export interface AuditDrawerProps {
	readonly event: AuditEvent | null;
	readonly currentUserId: string | null;
	readonly onClose: () => void;
}

export function AuditDrawer(props: AuditDrawerProps) {
	const { event, currentUserId, onClose } = props;
	const t = useTranslations("audit");

	return (
		<Dialog open={event !== null} onOpenChange={(next) => (next ? undefined : onClose())}>
			{event ? (
				<DialogContent className="max-w-3xl">
					<DialogHeader>
						<DialogTitle>{t(eventI18nKey(event.type))}</DialogTitle>
						<DialogDescription>
							<span className="font-mono text-xs">{event.id}</span>
						</DialogDescription>
					</DialogHeader>
					<DialogBody>
						<div className="flex flex-col gap-5">
							<ActorSection event={event} currentUserId={currentUserId} />
							<TargetSection event={event} />
							<DiffSection event={event} />
							<MetadataSection event={event} />
						</div>
					</DialogBody>
					<DialogFooter>
						<Button variant="outline" size="sm" onClick={onClose}>
							{t("drawerClose")}
						</Button>
					</DialogFooter>
				</DialogContent>
			) : null}
		</Dialog>
	);
}

function ActorSection(props: { event: AuditEvent; currentUserId: string | null }) {
	const { event, currentUserId } = props;
	const t = useTranslations("audit");
	const { actor } = event;
	const isSelf = actor.userId !== null && actor.userId === currentUserId;

	return (
		<SectionCard title={t("drawerSectionActor")}>
			{actor.isSystem ? (
				<p className="text-sm text-fg-secondary">{t("drawerActorSystem")}</p>
			) : (
				<dl className="grid grid-cols-3 gap-y-2 text-sm">
					<LabelCell label={t("drawerActorName")} />
					<dd className="col-span-2 text-fg-primary">
						{actor.displayName ?? t("drawerActorUnknown")}
						{isSelf ? (
							<Badge variant="info" size="sm" className="ml-2">
								{t("drawerActorSelf")}
							</Badge>
						) : null}
					</dd>
					<LabelCell label={t("drawerActorUsername")} />
					<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">
						{actor.username ?? "—"}
					</dd>
					<LabelCell label={t("drawerActorRoles")} />
					<dd className="col-span-2 flex flex-wrap gap-1">
						{actor.roles.length === 0 ? (
							<span className="text-fg-muted">—</span>
						) : (
							actor.roles.map((role) => (
								<Badge key={role} variant="secondary" size="sm">
									{role}
								</Badge>
							))
						)}
					</dd>
				</dl>
			)}
		</SectionCard>
	);
}

function TargetSection(props: { event: AuditEvent }) {
	const { event } = props;
	const t = useTranslations("audit");
	const typeLabel =
		event.target.type === "alert"
			? t("targetTypeAlert")
			: event.target.type === "setting"
				? t("targetTypeSetting")
				: t("targetTypeNotify");
	return (
		<SectionCard title={t("drawerSectionTarget")}>
			<dl className="grid grid-cols-3 gap-y-2 text-sm">
				<LabelCell label={t("drawerTargetType")} />
				<dd className="col-span-2 text-fg-primary">{typeLabel}</dd>
				<LabelCell label={t("drawerTargetId")} />
				<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">{event.target.id}</dd>
				<LabelCell label={t("drawerTargetLabel")} />
				<dd className="col-span-2 text-fg-primary">{event.target.label}</dd>
			</dl>
		</SectionCard>
	);
}

function DiffSection(props: { event: AuditEvent }) {
	const { event } = props;
	const t = useTranslations("audit");
	if (event.diff === null) {
		return (
			<SectionCard title={t("drawerSectionDiff")}>
				<p className="text-sm text-fg-muted">{t("drawerDiffNone")}</p>
			</SectionCard>
		);
	}
	return (
		<SectionCard title={t("drawerSectionDiff")}>
			<div className="grid grid-cols-1 gap-3 md:grid-cols-2">
				<DiffBlock title={t("drawerDiffBefore")} payload={event.diff.before} tone="critical" />
				<DiffBlock title={t("drawerDiffAfter")} payload={event.diff.after} tone="ok" />
			</div>
		</SectionCard>
	);
}

function DiffBlock(props: {
	readonly title: string;
	readonly payload: Readonly<Record<string, string | number | null>>;
	readonly tone: "critical" | "ok";
}) {
	const { title, payload, tone } = props;
	return (
		<div className="flex flex-col gap-2">
			<span className="text-xs font-medium uppercase tracking-wider text-fg-muted">{title}</span>
			<pre
				className={`overflow-auto rounded-md border border-border-hairline p-3 font-mono text-xs ${
					tone === "critical" ? "bg-sev-critical-bg text-sev-critical" : "bg-sev-ok-bg text-sev-ok"
				}`}
			>
				{JSON.stringify(payload, null, 2)}
			</pre>
		</div>
	);
}

function MetadataSection(props: { event: AuditEvent }) {
	const { event } = props;
	const t = useTranslations("audit");
	const { metadata } = event;
	const hasAny =
		metadata.engine !== undefined ||
		metadata.severity !== undefined ||
		metadata.status !== undefined ||
		metadata.channel !== undefined ||
		metadata.attempt !== undefined ||
		metadata.settingKey !== undefined;
	return (
		<SectionCard title={t("drawerSectionMetadata")}>
			<dl className="grid grid-cols-3 gap-y-2 text-sm">
				<LabelCell label={t("drawerMetaOccurredAt")} />
				<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">{event.occurredAt}</dd>
				<LabelCell label={t("drawerMetaEventType")} />
				<dd className="col-span-2 font-mono text-xs text-fg-secondary">{event.type}</dd>
				{metadata.engine ? (
					<>
						<LabelCell label={t("drawerMetaEngine")} />
						<dd className="col-span-2 text-fg-primary">{metadata.engine}</dd>
					</>
				) : null}
				{metadata.severity ? (
					<>
						<LabelCell label={t("drawerMetaSeverity")} />
						<dd className="col-span-2 text-fg-primary">{metadata.severity}</dd>
					</>
				) : null}
				{metadata.status ? (
					<>
						<LabelCell label={t("drawerMetaStatus")} />
						<dd className="col-span-2 text-fg-primary">{metadata.status}</dd>
					</>
				) : null}
				{metadata.channel ? (
					<>
						<LabelCell label={t("drawerMetaChannel")} />
						<dd className="col-span-2 text-fg-primary">{metadata.channel}</dd>
					</>
				) : null}
				{metadata.attempt !== undefined ? (
					<>
						<LabelCell label={t("drawerMetaAttempt")} />
						<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">
							{metadata.attempt}
						</dd>
					</>
				) : null}
				{metadata.settingKey ? (
					<>
						<LabelCell label={t("drawerMetaSettingKey")} />
						<dd className="col-span-2 font-mono text-fg-secondary">{metadata.settingKey}</dd>
					</>
				) : null}
			</dl>
			{hasAny ? null : <p className="text-sm text-fg-muted">{t("drawerMetaNone")}</p>}
		</SectionCard>
	);
}

function SectionCard(props: { title: string; children: React.ReactNode }) {
	return (
		<section className="rounded-md border border-border-hairline bg-bg-base p-4">
			<h3 className="mb-3 text-sm font-semibold text-fg-primary">{props.title}</h3>
			{props.children}
		</section>
	);
}

function LabelCell(props: { label: string }) {
	return (
		<dt className="text-xs font-medium uppercase tracking-wider text-fg-muted">{props.label}</dt>
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
