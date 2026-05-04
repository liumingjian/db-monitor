"use client";

import { type QuickMetricItem, QuickMetrics, useAutoRefresh } from "@db-monitor/ui";
import { useRouter } from "next/navigation";

const AUTO_REFRESH_INTERVAL_MS = 30_000;

export interface InstanceQuickMetricsProps {
	readonly items: readonly QuickMetricItem[];
}

/**
 * Q13 规则 2：顶部 Quick Metrics Strip + 30s auto-refresh。
 *
 * 通过 `router.refresh()` 触发当前 Server Component 重新渲染（重新拉 instance
 * + trend），避免在客户端私有维护 metric state 造成与 kill/filter server
 * action 的竞态。
 */
export function InstanceQuickMetrics(props: InstanceQuickMetricsProps) {
	const router = useRouter();
	useAutoRefresh(
		() => {
			router.refresh();
		},
		{ intervalMs: AUTO_REFRESH_INTERVAL_MS },
	);
	return <QuickMetrics items={props.items} />;
}
