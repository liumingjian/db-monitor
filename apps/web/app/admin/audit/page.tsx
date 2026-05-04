import { CanonicalPageTemplate, EntitySummary, PageContent, QuickMetrics } from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";

import { resolveActiveMembership } from "../../../src/auth";
import { AdminShell } from "../../../src/components/settings-audit/admin-shell";
import { buildAuditFeed } from "../../../src/components/settings-audit/audit-event-model";
import { AuditFeed } from "../../../src/components/settings-audit/audit-feed";
import { groupForHref, rootHrefForGroup } from "../../../src/components/shell/sidebar-groups";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

const AUDIT_FEED_LIMIT = 200;
const NOTIFY_FETCH_LIMIT = 50;

export default async function AuditPage() {
	const session = await requireServerSession("/admin/audit");
	const activeMembership = resolveActiveMembership(session);
	const canListUsers = activeMembership?.roles.includes("admin") ?? false;

	const apiClient = await createServerApiClient();
	const [alerts, settings, notifyHistory, users] = await Promise.all([
		apiClient.listAlerts(),
		apiClient.listSettings(),
		apiClient.listNotifyHistory({ limit: NOTIFY_FETCH_LIMIT }),
		canListUsers ? apiClient.listUsers() : Promise.resolve([]),
	]);

	const events = buildAuditFeed({
		alerts,
		settings,
		notifyHistory,
		users,
		limit: AUDIT_FEED_LIMIT,
	});

	const t = await getTranslations("audit");
	const tNav = await getTranslations("nav");

	const currentUser = users.find((user) => user.username === session.username) ?? null;

	const alertCount = events.filter((event) => event.target.type === "alert").length;
	const settingCount = events.filter((event) => event.target.type === "setting").length;
	const notifyCount = events.filter((event) => event.target.type === "notify").length;

	const rootGroup = groupForHref("/admin/audit");
	const breadcrumbs = [
		{ label: tNav(rootGroup), href: rootHrefForGroup(rootGroup) },
		{ label: t("breadcrumbAudit") },
	];

	return (
		<AdminShell
			breadcrumbs={breadcrumbs}
			userInitials={deriveInitials(session.displayName ?? session.username)}
		>
			<CanonicalPageTemplate>
				<EntitySummary
					title={t("title")}
					subtitle={t("subtitle")}
					badges={[{ tone: "info", label: "read-only" }]}
				/>
				<QuickMetrics
					items={[
						{
							key: "events",
							label: t("quickMetricEvents"),
							value: String(events.length),
						},
						{
							key: "alerts",
							label: t("quickMetricAlerts"),
							value: String(alertCount),
						},
						{
							key: "settings",
							label: t("quickMetricSettings"),
							value: String(settingCount),
						},
						{
							key: "notify",
							label: t("quickMetricNotify"),
							value: String(notifyCount),
						},
					]}
				/>
				<PageContent>
					<AuditFeed
						events={events}
						limit={AUDIT_FEED_LIMIT}
						currentUserId={currentUser?.user_id ?? null}
					/>
				</PageContent>
			</CanonicalPageTemplate>
		</AdminShell>
	);
}

function deriveInitials(value: string | null): string {
	if (value === null || value.trim().length === 0) {
		return "DB";
	}
	const [first = "", second = ""] = value.split(/\s+/);
	if (first.length === 0) {
		return "DB";
	}
	return (first[0] ?? "").toUpperCase() + (second[0] ?? "").toUpperCase();
}
