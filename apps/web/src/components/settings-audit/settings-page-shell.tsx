"use client";

import { useTranslations } from "next-intl";
import { useState } from "react";
import type { ReactNode } from "react";

import type { SettingsGroupId } from "./settings-group-model";
import { SettingsSideNav, type SettingsSideNavEntry } from "./settings-side-nav";

export interface SettingsPageShellProps {
	readonly groups: Readonly<Record<SettingsGroupId, ReactNode>>;
	readonly counts: Readonly<Record<SettingsGroupId, number>>;
}

export function SettingsPageShell(props: SettingsPageShellProps) {
	const { groups, counts } = props;
	const t = useTranslations("settingsPage");
	const [activeId, setActiveId] = useState<SettingsGroupId>("general");

	const entries: readonly SettingsSideNavEntry[] = [
		{
			id: "general",
			label: t("sideNavGeneral"),
			description: t("sideNavGeneralDesc"),
			count: counts.general,
		},
		{
			id: "retention",
			label: t("sideNavRetention"),
			description: t("sideNavRetentionDesc"),
			count: counts.retention,
		},
		{
			id: "notifications",
			label: t("sideNavNotifications"),
			description: t("sideNavNotificationsDesc"),
			count: counts.notifications,
		},
		{
			id: "integrations",
			label: t("sideNavIntegrations"),
			description: t("sideNavIntegrationsDesc"),
			count: counts.integrations,
		},
		{
			id: "advanced",
			label: t("sideNavAdvanced"),
			description: t("sideNavAdvancedDesc"),
			count: counts.advanced,
		},
		{
			id: "about",
			label: t("sideNavAbout"),
			description: t("sideNavAboutDesc"),
			count: counts.about,
		},
	];

	return (
		<div className="grid gap-6 md:grid-cols-[240px_1fr]">
			<aside className="md:sticky md:top-4 md:self-start">
				<SettingsSideNav entries={entries} activeId={activeId} onSelect={setActiveId} />
			</aside>
			<section className="flex flex-col gap-4">{groups[activeId]}</section>
		</div>
	);
}
