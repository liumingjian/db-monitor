import type { ReactNode } from "react";

import { AppChrome } from "../../../src/components/app-chrome";
import {
	type InstanceTabDescriptor,
	InstanceTabNav,
} from "../../../src/components/instance-tab-nav";
import { requireServerSession } from "../../../src/server-api";

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
	const tabs = buildInstanceTabs(instanceId);

	return (
		<AppChrome session={session}>
			<div className="space-y-6">
				<InstanceTabNav tabs={tabs} />
				{children}
			</div>
		</AppChrome>
	);
}

function buildInstanceTabs(instanceId: string): readonly InstanceTabDescriptor[] {
	return [
		{
			href: `/instances/${instanceId}`,
			label: "Overview",
			segment: "overview",
		},
		{
			href: `/instances/${instanceId}/processes`,
			label: "Processes",
			segment: "processes",
		},
	];
}
