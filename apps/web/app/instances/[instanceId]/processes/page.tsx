import {
	buildProcesslistFilterValues,
	buildProcesslistViewModel,
	hasKillPermission,
	toProcesslistApiFilters,
} from "../../../../src/processlist-ui";
import { createServerApiClient } from "../../../../src/server-api";
import { ProcesslistEmptyStateBanner } from "../_components/processlist-empty-state";
import { ProcesslistFilterForm } from "../_components/processlist-filter-form";
import { ProcesslistTable } from "../_components/processlist-table";

interface ProcessesPageProps {
	readonly params: Promise<{
		readonly instanceId: string;
	}>;
	readonly searchParams: Promise<{
		readonly user?: string;
		readonly host?: string;
		readonly command?: string;
		readonly minTimeSeconds?: string;
		readonly collectedAfter?: string;
		readonly collectedBefore?: string;
		readonly limit?: string;
	}>;
}

export default async function ProcessesPage({ params, searchParams }: ProcessesPageProps) {
	const { instanceId } = await params;
	const resolvedSearchParams = await searchParams;
	const filters = buildProcesslistFilterValues(resolvedSearchParams);
	const apiClient = await createServerApiClient();
	const [instance, snapshot, permissions] = await Promise.all([
		apiClient.getInstance(instanceId),
		apiClient.getInstanceProcesslist(instanceId, toProcesslistApiFilters(filters)),
		resolvePermissions(apiClient),
	]);
	const model = buildProcesslistViewModel(instance, snapshot, filters);
	const canKill = hasKillPermission(permissions);
	const formAction = `/instances/${instanceId}/processes`;

	return (
		<section aria-labelledby="processlist-heading" className="space-y-4">
			<header className="flex flex-wrap items-baseline justify-between gap-3">
				<div>
					<h2 className="text-2xl font-semibold" id="processlist-heading">
						Processes
					</h2>
					<p className="mt-1 text-sm text-[var(--muted)]">
						最新采集: <span className="font-mono">{model.snapshotLabel}</span>
					</p>
				</div>
				<p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
					{model.entries.length} sessions
				</p>
			</header>
			<ProcesslistFilterForm action={formAction} filters={model.filters} />
			{model.emptyState === null ? (
				<ProcesslistTable
					canKill={canKill}
					entries={model.entries}
					instanceId={instanceId}
					monitorUsername={instance.connection.username}
					validationPassed={model.validationPassed}
				/>
			) : (
				<ProcesslistEmptyStateBanner state={model.emptyState} />
			)}
		</section>
	);
}

async function resolvePermissions(
	apiClient: Awaited<ReturnType<typeof createServerApiClient>>,
): Promise<readonly string[]> {
	const session = await apiClient.me();
	return session.permissions;
}
