"use client";

import {
	NotificationDrawer,
	type NotificationEntry,
	type NotificationTabConfig,
	type NotificationTabKey,
} from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { type ReactNode, createContext, useCallback, useContext, useMemo, useState } from "react";

export interface NotificationCenterState {
	readonly open: boolean;
	readonly setOpen: (next: boolean) => void;
	readonly activeTab: NotificationTabKey;
	readonly setActiveTab: (next: NotificationTabKey) => void;
	readonly alerts: readonly NotificationEntry[];
	readonly notifyDeliveries: readonly NotificationEntry[];
	readonly systemMessages: readonly NotificationEntry[];
	readonly setAlerts: (entries: readonly NotificationEntry[]) => void;
	readonly setNotifyDeliveries: (entries: readonly NotificationEntry[]) => void;
	readonly setSystemMessages: (entries: readonly NotificationEntry[]) => void;
	readonly unreadCount: number;
}

const NotificationCenterContext = createContext<NotificationCenterState | null>(null);

export function useNotificationCenter(): NotificationCenterState {
	const ctx = useContext(NotificationCenterContext);
	if (!ctx) {
		throw new Error("useNotificationCenter must be used within <NotificationCenterProvider>.");
	}
	return ctx;
}

export function NotificationCenterProvider(props: { readonly children: ReactNode }) {
	const [open, setOpen] = useState(false);
	const [activeTab, setActiveTab] = useState<NotificationTabKey>("alerts");
	const [alerts, setAlerts] = useState<readonly NotificationEntry[]>([]);
	const [notifyDeliveries, setNotifyDeliveries] = useState<readonly NotificationEntry[]>([]);
	const [systemMessages, setSystemMessages] = useState<readonly NotificationEntry[]>([]);

	const unreadCount = alerts.length + notifyDeliveries.length + systemMessages.length;

	const value = useMemo<NotificationCenterState>(
		() => ({
			open,
			setOpen,
			activeTab,
			setActiveTab,
			alerts,
			notifyDeliveries,
			systemMessages,
			setAlerts,
			setNotifyDeliveries,
			setSystemMessages,
			unreadCount,
		}),
		[open, activeTab, alerts, notifyDeliveries, systemMessages, unreadCount],
	);

	return (
		<NotificationCenterContext.Provider value={value}>
			{props.children}
		</NotificationCenterContext.Provider>
	);
}

export function AppNotificationDrawer() {
	const t = useTranslations("notifications");
	const state = useNotificationCenter();

	const tabs = useMemo<readonly NotificationTabConfig[]>(
		() => [
			{
				key: "alerts",
				label: t("tabAlerts"),
				entries: state.alerts,
				emptyLabel: t("emptyAlerts"),
			},
			{
				key: "notify",
				label: t("tabNotifyHistory"),
				entries: state.notifyDeliveries,
				emptyLabel: t("emptyNotifyHistory"),
			},
			{
				key: "system",
				label: t("tabSystem"),
				entries: state.systemMessages,
				emptyLabel: t("emptySystem"),
			},
		],
		[t, state.alerts, state.notifyDeliveries, state.systemMessages],
	);

	const onOpenChange = useCallback(
		(next: boolean) => {
			state.setOpen(next);
		},
		[state],
	);

	const onActiveTabChange = useCallback(
		(next: NotificationTabKey) => {
			state.setActiveTab(next);
		},
		[state],
	);

	return (
		<NotificationDrawer
			open={state.open}
			onOpenChange={onOpenChange}
			activeTab={state.activeTab}
			onActiveTabChange={onActiveTabChange}
			tabs={tabs}
			strings={{
				title: t("title"),
				close: t("close"),
				viewAll: t("viewAll"),
			}}
		/>
	);
}
