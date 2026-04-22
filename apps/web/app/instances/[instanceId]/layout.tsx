import type { ReactNode } from "react";

import { AppChrome } from "../../../src/components/app-chrome";
import {
	type InstanceTabDescriptor,
	InstanceTabNav,
} from "../../../src/components/instance-tab-nav";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

interface InstanceDetailLayoutProps {
	readonly children: ReactNode;
	readonly params: Promise<{
		readonly instanceId: string;
	}>;
}

export default async function InstanceDetailLayout({
	children,
	params,
}: InstanceDetailLayoutProps) {
	const { instanceId } = await params;
	const session = await requireServerSession(`/instances/${instanceId}`);
	const apiClient = await createServerApiClient();
	const instance = await apiClient.getInstance(instanceId);
	const tabs = buildInstanceTabs({
		instanceId,
		engine: instance.engine,
	});

	return (
		<AppChrome session={session}>
			<div className="space-y-6">
				<InstanceTabNav tabs={tabs} />
				{children}
			</div>
		</AppChrome>
	);
}

interface InstanceTabsInput {
	readonly instanceId: string;
	readonly engine: "mysql" | "oracle";
}

function buildInstanceTabs(
	input: InstanceTabsInput,
): readonly InstanceTabDescriptor[] {
	const tabs: InstanceTabDescriptor[] = [
		{
			href: `/instances/${input.instanceId}`,
			label: "Overview",
			segment: "overview",
		},
		{
			href: `/instances/${input.instanceId}/processes`,
			label: "Processes",
			segment: "processes",
		},
	];
	if (input.engine === "mysql") {
		tabs.push({
			href: `/instances/${input.instanceId}/slow-queries`,
			label: "Slow queries",
			segment: "slow-queries",
		});
	}
	if (input.engine === "oracle") {
		tabs.push({
			href: `/instances/${input.instanceId}/tablespaces`,
			label: "表空间",
			segment: "tablespaces",
		});
	}
	return tabs;
}
