"use client";

import { TabBar, type TabItem } from "@db-monitor/ui";
import { usePathname } from "next/navigation";

import type { InstanceTabDescriptor, InstanceTabKey } from "./instance-tabs";

export interface InstanceTabsBarProps {
	readonly instanceId: string;
	readonly tabs: readonly InstanceTabDescriptor[];
}

/**
 * Client tab bar — picks active key from usePathname(). Kept client-only so
 * server layout can stay a pure data loader.
 */
export function InstanceTabsBar(props: InstanceTabsBarProps) {
	const pathname = usePathname() ?? "";
	const activeKey = resolveActiveKey(pathname, props.instanceId, props.tabs);
	const items: readonly TabItem[] = props.tabs.map((tab) => ({
		href: tab.href,
		key: tab.key,
		label: tab.label,
	}));
	return <TabBar activeKey={activeKey} tabs={items} />;
}

function resolveActiveKey(
	pathname: string,
	instanceId: string,
	tabs: readonly InstanceTabDescriptor[],
): InstanceTabKey {
	const base = `/instances/${instanceId}`;
	const remainder = pathname.startsWith(base) ? pathname.slice(base.length) : "";
	const firstSegment = remainder.replace(/^\//, "").split("/")[0] ?? "";
	if (firstSegment.length === 0) {
		return "overview";
	}
	const match = tabs.find((tab) => tab.segment === firstSegment);
	return match?.key ?? "overview";
}
