import { API_CONTRACT_VERSION } from "@db-monitor/api-client";
import {
	Badge,
	CanonicalPageTemplate,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	EntitySummary,
	PageBreadcrumb,
	PageContent,
	QuickMetrics,
} from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";
import type { ReactNode } from "react";

import { resolveActiveMembership } from "../../src/auth";
import { AdminShell } from "../../src/components/settings-audit/admin-shell";
import { SettingsGroupEmpty } from "../../src/components/settings-audit/settings-group-empty";
import {
	type SettingsGroupId,
	partitionSettings,
} from "../../src/components/settings-audit/settings-group-model";
import { SettingsKeyValueForm } from "../../src/components/settings-audit/settings-key-value-form";
import { SettingsPageShell } from "../../src/components/settings-audit/settings-page-shell";
import { UserRoleCard } from "../../src/components/settings-audit/user-role-card";
import { createServerApiClient, requireServerSession } from "../../src/server-api";
import { buildSettingsManagementModel } from "../../src/settings-management";

export default async function SettingsPage() {
	const session = await requireServerSession("/settings");
	const activeMembership = resolveActiveMembership(session);
	const canManageUsers = activeMembership?.roles.includes("admin") ?? false;

	const apiClient = await createServerApiClient();
	const [settings, users, roleCatalog] = await Promise.all([
		apiClient.listSettings(),
		canManageUsers ? apiClient.listUsers() : Promise.resolve([]),
		canManageUsers ? apiClient.listRoleCatalog() : Promise.resolve([]),
	]);
	const managementModel = buildSettingsManagementModel({
		activeMembership,
		roleCatalog,
		users,
	});

	const t = await getTranslations("settingsPage");
	const partitions = partitionSettings(settings);

	const formLabels = {
		keyLabel: t("keyLabel"),
		valueLabel: t("valueLabel"),
		updatedAt: t("updatedAt"),
		save: t("save"),
		permissionDenied: t("permissionDenied"),
	};

	const userLabels = {
		activeOrg: t("advancedUserActiveOrg"),
		permissions: t("advancedUserPermissions"),
		noPermissions: t("advancedUserNoPermissions"),
		updateRoles: t("advancedUpdateRoles"),
	};

	const groups: Record<SettingsGroupId, ReactNode> = {
		general: (
			<GeneralGroup
				orgName={session.activeOrganization?.name ?? "—"}
				orgSlug={session.activeOrganization?.slug ?? "—"}
				membershipCount={session.organizationMemberships.length}
				roles={activeMembership?.roles ?? []}
				username={session.username}
				displayName={session.displayName}
				labels={{
					orgTitle: t("generalOrgTitle"),
					orgSlug: t("generalOrgSlug"),
					orgMembershipCount: (count: number) => t("generalOrgMembershipCount", { count }),
					orgNoRoles: t("generalOrgNoRoles"),
					selfTitle: t("generalSelfTitle"),
					selfUsername: t("generalSelfUsername"),
					selfDisplayName: t("generalSelfDisplayName"),
					membershipsTitle: t("generalMembershipsTitle"),
					membershipActive: t("generalMembershipActive"),
					preferencesTitle: t("generalPreferencesTitle"),
					preferencesTheme: t("generalPreferencesTheme"),
					preferencesThemeHint: t("generalPreferencesThemeHint"),
					preferencesLanguage: t("generalPreferencesLanguage"),
					preferencesLanguageValue: t("generalPreferencesLanguageValue"),
				}}
				memberships={session.organizationMemberships.map((membership) => ({
					organizationId: membership.organization.organization_id,
					name: membership.organization.name,
					slug: membership.organization.slug,
					roles: membership.roles,
					isActive:
						membership.organization.organization_id === session.activeOrganization?.organization_id,
				}))}
			/>
		),
		retention: (
			<GroupList
				title={t("retentionTitle")}
				hint={t("retentionHint")}
				settings={partitions.retention}
				canWrite={canManageUsers}
				formLabels={formLabels}
				emptyTitle={t("emptyTitle")}
				emptyHint={t("emptyHint")}
			/>
		),
		notifications: (
			<GroupList
				title={t("notificationsTitle")}
				hint={t("notificationsHint")}
				settings={partitions.notifications}
				canWrite={canManageUsers}
				formLabels={formLabels}
				emptyTitle={t("emptyTitle")}
				emptyHint={t("emptyHint")}
				footer={
					<a
						href="/admin/channels"
						className="inline-flex items-center text-sm text-accent underline-offset-4 hover:underline"
					>
						{t("notificationsGoChannels")}
					</a>
				}
			/>
		),
		integrations: (
			<GroupList
				title={t("integrationsTitle")}
				hint={t("integrationsHint")}
				settings={partitions.integrations}
				canWrite={canManageUsers}
				formLabels={formLabels}
				emptyTitle={t("integrationsEmpty")}
				emptyHint={t("integrationsEmptyHint")}
			/>
		),
		advanced: (
			<AdvancedGroup
				title={t("advancedTitle")}
				hint={t("advancedHint")}
				usersTitle={t("advancedUsersTitle")}
				rolesTitle={t("advancedRolesCatalog")}
				rolesHint={t("advancedRolesCatalogHint")}
				usersEmpty={t("advancedUsersEmpty")}
				readOnly={t("advancedReadOnly")}
				emptyTitle={t("emptyTitle")}
				emptyHint={t("emptyHint")}
				settings={partitions.advanced}
				users={managementModel.users}
				roleCatalog={managementModel.roleCatalog}
				canWrite={canManageUsers}
				formLabels={formLabels}
				userLabels={userLabels}
			/>
		),
		about: (
			<AboutGroup
				title={t("aboutTitle")}
				contractVersionLabel={t("aboutContractVersion")}
				sliceLabel={t("aboutSlice")}
				sliceValue={t("aboutSliceValue")}
				adrTitle={t("aboutAdrTitle")}
				adr0012={t("aboutAdr0012")}
				adr0006={t("aboutAdr0006")}
				adr0004={t("aboutAdr0004")}
			/>
		),
	};

	const counts: Record<SettingsGroupId, number> = {
		general: 4,
		retention: partitions.retention.length,
		notifications: partitions.notifications.length,
		integrations: partitions.integrations.length,
		advanced: partitions.advanced.length + (canManageUsers ? managementModel.users.length : 0),
		about: 3,
	};

	return (
		<AdminShell
			breadcrumbs={[
				{ label: t("breadcrumbAdmin"), href: "/settings" },
				{ label: t("breadcrumbSettings") },
			]}
			userInitials={deriveInitials(session.displayName ?? session.username)}
		>
			<CanonicalPageTemplate>
				<PageBreadcrumb
					items={[
						{ label: t("breadcrumbAdmin"), href: "/settings" },
						{ label: t("breadcrumbSettings") },
					]}
				/>
				<EntitySummary
					title={t("title")}
					subtitle={t("subtitle")}
					badges={[
						{
							tone: canManageUsers ? "ok" : "info",
							label: canManageUsers ? "admin" : "read-only",
						},
					]}
				/>
				<QuickMetrics
					items={[
						{
							key: "org",
							label: t("quickMetricOrg"),
							value: session.activeOrganization?.name ?? "—",
						},
						{
							key: "membership",
							label: t("quickMetricMembership"),
							value: String(session.organizationMemberships.length),
						},
						{
							key: "roles",
							label: t("quickMetricRoles"),
							value:
								(activeMembership?.roles.length ?? 0) === 0
									? "—"
									: (activeMembership?.roles.join(" / ") ?? "—"),
						},
						{
							key: "settings",
							label: t("quickMetricKeys"),
							value: String(settings.length),
						},
					]}
				/>
				<PageContent>
					<SettingsPageShell groups={groups} counts={counts} />
				</PageContent>
			</CanonicalPageTemplate>
		</AdminShell>
	);
}

interface GeneralGroupLabels {
	readonly orgTitle: string;
	readonly orgSlug: string;
	readonly orgMembershipCount: (count: number) => string;
	readonly orgNoRoles: string;
	readonly selfTitle: string;
	readonly selfUsername: string;
	readonly selfDisplayName: string;
	readonly membershipsTitle: string;
	readonly membershipActive: string;
	readonly preferencesTitle: string;
	readonly preferencesTheme: string;
	readonly preferencesThemeHint: string;
	readonly preferencesLanguage: string;
	readonly preferencesLanguageValue: string;
}

interface GeneralGroupProps {
	readonly orgName: string;
	readonly orgSlug: string;
	readonly membershipCount: number;
	readonly roles: readonly string[];
	readonly username: string | null;
	readonly displayName: string | null;
	readonly memberships: readonly {
		readonly organizationId: string;
		readonly name: string;
		readonly slug: string;
		readonly roles: readonly string[];
		readonly isActive: boolean;
	}[];
	readonly labels: GeneralGroupLabels;
}

function GeneralGroup(props: GeneralGroupProps) {
	const { orgName, orgSlug, membershipCount, roles, username, displayName, memberships, labels } =
		props;
	return (
		<>
			<Card>
				<CardHeader>
					<CardTitle>{labels.orgTitle}</CardTitle>
					<CardDescription>{labels.orgMembershipCount(membershipCount)}</CardDescription>
				</CardHeader>
				<CardContent className="flex flex-col gap-3">
					<dl className="grid grid-cols-3 gap-y-2 text-sm">
						<dt className="text-xs uppercase tracking-wider text-fg-muted">{labels.orgSlug}</dt>
						<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">{orgSlug}</dd>
					</dl>
					<div className="flex flex-wrap gap-1.5">
						{roles.length === 0 ? (
							<Badge variant="outline" size="sm">
								{labels.orgNoRoles}
							</Badge>
						) : (
							roles.map((role) => (
								<Badge key={role} variant="secondary" size="sm">
									{role}
								</Badge>
							))
						)}
					</div>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>{labels.selfTitle}</CardTitle>
				</CardHeader>
				<CardContent>
					<dl className="grid grid-cols-3 gap-y-2 text-sm">
						<dt className="text-xs uppercase tracking-wider text-fg-muted">
							{labels.selfUsername}
						</dt>
						<dd className="col-span-2 font-mono text-fg-secondary">{username ?? "—"}</dd>
						<dt className="text-xs uppercase tracking-wider text-fg-muted">
							{labels.selfDisplayName}
						</dt>
						<dd className="col-span-2 text-fg-primary">{displayName ?? "—"}</dd>
					</dl>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>{labels.membershipsTitle}</CardTitle>
				</CardHeader>
				<CardContent>
					<ul className="flex flex-col gap-2">
						{memberships.map((membership) => (
							<li
								key={membership.organizationId}
								className="flex items-start justify-between gap-3 rounded-md border border-border-hairline bg-bg-base px-3 py-2"
							>
								<div>
									<p className="text-sm font-medium text-fg-primary">{membership.name}</p>
									<p className="font-mono text-xs text-fg-muted">{membership.slug}</p>
									<p className="mt-1 text-xs text-fg-secondary">
										roles: {membership.roles.join(", ") || "—"}
									</p>
								</div>
								{membership.isActive ? (
									<Badge variant="ok" size="sm">
										{labels.membershipActive}
									</Badge>
								) : null}
							</li>
						))}
					</ul>
				</CardContent>
			</Card>

			<Card>
				<CardHeader>
					<CardTitle>{labels.preferencesTitle}</CardTitle>
				</CardHeader>
				<CardContent>
					<dl className="grid grid-cols-3 gap-y-2 text-sm">
						<dt className="text-xs uppercase tracking-wider text-fg-muted">
							{labels.preferencesTheme}
						</dt>
						<dd className="col-span-2 text-fg-secondary">{labels.preferencesThemeHint}</dd>
						<dt className="text-xs uppercase tracking-wider text-fg-muted">
							{labels.preferencesLanguage}
						</dt>
						<dd className="col-span-2 text-fg-primary">{labels.preferencesLanguageValue}</dd>
					</dl>
				</CardContent>
			</Card>
		</>
	);
}

interface GroupListProps {
	readonly title: string;
	readonly hint: string;
	readonly settings: readonly import("@db-monitor/api-client").SystemSettingResponse[];
	readonly canWrite: boolean;
	readonly formLabels: {
		readonly keyLabel: string;
		readonly valueLabel: string;
		readonly updatedAt: string;
		readonly save: string;
		readonly permissionDenied: string;
	};
	readonly emptyTitle: string;
	readonly emptyHint: string;
	readonly footer?: ReactNode;
}

function GroupList(props: GroupListProps) {
	const { title, hint, settings, canWrite, formLabels, emptyTitle, emptyHint, footer } = props;
	return (
		<>
			<Card>
				<CardHeader>
					<CardTitle>{title}</CardTitle>
					<CardDescription>{hint}</CardDescription>
				</CardHeader>
			</Card>
			{settings.length === 0 ? (
				<SettingsGroupEmpty title={emptyTitle} hint={emptyHint} />
			) : (
				settings.map((setting) => (
					<SettingsKeyValueForm
						key={setting.key}
						setting={setting}
						canWrite={canWrite}
						labels={formLabels}
					/>
				))
			)}
			{footer ? <div className="pt-2">{footer}</div> : null}
		</>
	);
}

interface AdvancedGroupProps {
	readonly title: string;
	readonly hint: string;
	readonly usersTitle: string;
	readonly rolesTitle: string;
	readonly rolesHint: string;
	readonly usersEmpty: string;
	readonly readOnly: string;
	readonly emptyTitle: string;
	readonly emptyHint: string;
	readonly settings: readonly import("@db-monitor/api-client").SystemSettingResponse[];
	readonly users: readonly import("@db-monitor/api-client").ManagedUserResponse[];
	readonly roleCatalog: readonly import("@db-monitor/api-client").RoleCatalogEntryResponse[];
	readonly canWrite: boolean;
	readonly formLabels: GroupListProps["formLabels"];
	readonly userLabels: {
		readonly activeOrg: string;
		readonly permissions: string;
		readonly noPermissions: string;
		readonly updateRoles: string;
	};
}

function AdvancedGroup(props: AdvancedGroupProps) {
	const {
		title,
		hint,
		usersTitle,
		rolesTitle,
		rolesHint,
		usersEmpty,
		readOnly,
		emptyTitle,
		emptyHint,
		settings,
		users,
		roleCatalog,
		canWrite,
		formLabels,
		userLabels,
	} = props;
	return (
		<>
			<Card>
				<CardHeader>
					<CardTitle>{title}</CardTitle>
					<CardDescription>{hint}</CardDescription>
				</CardHeader>
			</Card>
			{settings.length === 0 ? (
				<SettingsGroupEmpty title={emptyTitle} hint={emptyHint} />
			) : (
				settings.map((setting) => (
					<SettingsKeyValueForm
						key={setting.key}
						setting={setting}
						canWrite={canWrite}
						labels={formLabels}
					/>
				))
			)}

			<Card>
				<CardHeader>
					<CardTitle>{usersTitle}</CardTitle>
					<CardDescription>{canWrite ? hint : readOnly}</CardDescription>
				</CardHeader>
				<CardContent>
					{canWrite ? (
						users.length === 0 ? (
							<p className="text-sm text-fg-muted">{usersEmpty}</p>
						) : (
							<div className="flex flex-col gap-3">
								{users.map((user) => (
									<UserRoleCard
										key={user.user_id}
										user={user}
										roleCatalog={roleCatalog}
										labels={userLabels}
									/>
								))}
							</div>
						)
					) : (
						<p className="text-sm text-fg-muted">{readOnly}</p>
					)}
				</CardContent>
			</Card>

			{canWrite && roleCatalog.length > 0 ? (
				<Card>
					<CardHeader>
						<CardTitle>{rolesTitle}</CardTitle>
						<CardDescription>{rolesHint}</CardDescription>
					</CardHeader>
					<CardContent className="flex flex-col gap-2">
						{roleCatalog.map((entry) => (
							<div
								key={entry.role}
								className="flex flex-col gap-1 rounded-md border border-border-hairline bg-bg-base px-3 py-2"
							>
								<span className="text-sm font-medium capitalize text-fg-primary">{entry.role}</span>
								<span className="text-xs text-fg-muted">{entry.permissions.join(", ") || "—"}</span>
							</div>
						))}
					</CardContent>
				</Card>
			) : null}
		</>
	);
}

interface AboutGroupProps {
	readonly title: string;
	readonly contractVersionLabel: string;
	readonly sliceLabel: string;
	readonly sliceValue: string;
	readonly adrTitle: string;
	readonly adr0012: string;
	readonly adr0006: string;
	readonly adr0004: string;
}

function AboutGroup(props: AboutGroupProps) {
	const {
		title,
		contractVersionLabel,
		sliceLabel,
		sliceValue,
		adrTitle,
		adr0012,
		adr0006,
		adr0004,
	} = props;
	return (
		<Card>
			<CardHeader>
				<CardTitle>{title}</CardTitle>
			</CardHeader>
			<CardContent>
				<dl className="grid grid-cols-3 gap-y-2 text-sm">
					<dt className="text-xs uppercase tracking-wider text-fg-muted">{contractVersionLabel}</dt>
					<dd className="col-span-2 font-mono tabular-nums text-fg-secondary">
						{API_CONTRACT_VERSION}
					</dd>
					<dt className="text-xs uppercase tracking-wider text-fg-muted">{sliceLabel}</dt>
					<dd className="col-span-2 text-fg-primary">{sliceValue}</dd>
				</dl>
				<h4 className="mt-4 text-xs font-medium uppercase tracking-wider text-fg-muted">
					{adrTitle}
				</h4>
				<ul className="mt-2 flex flex-col gap-1 text-sm">
					<li className="font-mono text-fg-secondary">{adr0012}</li>
					<li className="font-mono text-fg-secondary">{adr0006}</li>
					<li className="font-mono text-fg-secondary">{adr0004}</li>
				</ul>
			</CardContent>
		</Card>
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
