import { CanonicalPageTemplate, EntitySummary, PageBreadcrumb } from "@db-monitor/ui";
import type { EntityBadgeModel } from "@db-monitor/ui";
import type { ReactNode } from "react";

import { InstanceDetailShell } from "../../../src/components/instance-detail/instance-detail-shell";
import { buildInstanceQuickMetricItems } from "../../../src/components/instance-detail/instance-metrics";
import { InstanceQuickMetrics } from "../../../src/components/instance-detail/instance-quick-metrics";
import { buildInstanceTabs } from "../../../src/components/instance-detail/instance-tabs";
import { InstanceTabsBar } from "../../../src/components/instance-detail/instance-tabs-bar";
import {
	createServerApiClient,
	parseTimeWindow,
	requireServerSession,
} from "../../../src/server-api";

interface InstanceDetailLayoutProps {
	readonly children: ReactNode;
	readonly params: Promise<{ readonly instanceId: string }>;
}

export default async function InstanceDetailLayout({
	children,
	params,
}: InstanceDetailLayoutProps) {
	const { instanceId } = await params;
	const session = await requireServerSession(`/instances/${instanceId}`);
	const apiClient = await createServerApiClient();
	const instance = await apiClient.getInstance(instanceId);
	const trend = await safeLoadTrend(apiClient, instanceId);
	const tabs = buildInstanceTabs({ engine: instance.engine, instanceId });
	const badges = buildInstanceBadges(instance);
	const metricItems = buildInstanceQuickMetricItems({ instance, trend });

	return (
		<InstanceDetailShell instanceName={instance.name} session={session}>
			<CanonicalPageTemplate>
				<PageBreadcrumb
					items={[
						{ href: "/overview", label: "观测" },
						{ href: "/instances", label: "实例" },
						{ label: instance.name },
					]}
				/>
				<EntitySummary
					badges={badges}
					subtitle={`${instance.connection.host}:${instance.connection.port} · ${instance.connection.database}`}
					title={instance.name}
				/>
				<InstanceQuickMetrics items={metricItems} />
				<InstanceTabsBar instanceId={instanceId} tabs={tabs} />
				{children}
			</CanonicalPageTemplate>
		</InstanceDetailShell>
	);
}

function buildInstanceBadges(instance: {
	readonly engine: "mysql" | "oracle";
	readonly environment: string;
	readonly validation: { readonly status: string };
}): readonly EntityBadgeModel[] {
	const validation = instance.validation.status;
	const validationTone: EntityBadgeModel["tone"] =
		validation === "passed" ? "ok" : validation === "failed" ? "critical" : "warning";
	const validationLabel =
		validation === "passed" ? "校验通过" : validation === "failed" ? "校验失败" : "校验中";
	return [
		{ label: instance.environment.toUpperCase(), tone: "info" },
		{ label: instance.engine.toUpperCase(), tone: "info" },
		{ label: validationLabel, tone: validationTone },
	];
}

async function safeLoadTrend(
	apiClient: Awaited<ReturnType<typeof createServerApiClient>>,
	instanceId: string,
) {
	try {
		return await apiClient.getInstanceTrends(instanceId, parseTimeWindow(undefined));
	} catch {
		// Trend endpoint may return 5xx while采集尚未就绪；不阻塞整张详情页，但显示 "—"
		// 表示该 metric 未上报（非 silent fallback：调用方会看到占位符而不是假数据）。
		return null;
	}
}
