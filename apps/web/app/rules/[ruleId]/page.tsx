import Link from "next/link";

import { AppChrome } from "../../../src/components/app-chrome";
import { toDraftRows } from "../../../src/rule-overrides-ui";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

import { RuleEditForm } from "./_components/rule-edit-form";

interface RuleEditPageProps {
	readonly params: Promise<{ readonly ruleId: string }>;
	readonly searchParams: Promise<{ readonly saved?: string }>;
}

export default async function RuleEditPage({ params, searchParams }: RuleEditPageProps) {
	const { ruleId } = await params;
	const { saved } = await searchParams;
	const session = await requireServerSession(`/rules/${ruleId}`);
	const apiClient = await createServerApiClient();
	const [rule, instances] = await Promise.all([
		apiClient.getRule(ruleId),
		apiClient.listInstances({ status: "passed" }),
	]);
	const engineInstances = instances.filter((instance) => instance.engine === rule.engine);
	const initialRows = toDraftRows(rule.overrides);

	return (
		<AppChrome session={session}>
			<div className="space-y-6">
				<header className="flex flex-wrap items-baseline justify-between gap-3">
					<div>
						<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
							<Link href="/rules">← 返回规则列表</Link>
						</p>
						<h2 className="mt-2 text-2xl font-semibold">编辑规则：{rule.name}</h2>
						<p className="mt-1 text-sm text-[var(--muted)]">
							{rule.engine} · {rule.metric_name} · 默认阈值 {rule.threshold}
						</p>
					</div>
					{saved === "1" ? (
						<output className="rounded-[0.8rem] border border-green-500/30 bg-green-50 px-3 py-2 text-xs font-semibold text-green-700">
							已保存覆盖配置
						</output>
					) : null}
				</header>
				<RuleEditForm
					initialRows={initialRows}
					instances={engineInstances.map((instance) => ({
						id: instance.instance_id,
						label: `${instance.name} (${instance.instance_id})`,
					}))}
					ruleId={rule.rule_id}
				/>
			</div>
		</AppChrome>
	);
}
