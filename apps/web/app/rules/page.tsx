import Link from "next/link";

import { RULE_OPERATORS, RULE_SEVERITIES } from "@db-monitor/ui";
import { AppChrome } from "../../src/components/app-chrome";

import { createRuleAction } from "../../src/monitoring-actions";
import { buildOperationsModel, formatDatabaseEngine } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

export default async function RulesPage() {
	const session = await requireServerSession("/rules");
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		ruleCatalog: await apiClient.listRuleCatalog(),
		rules: await apiClient.listRules(),
	});

	return (
		<AppChrome session={session}>
			<div className="grid gap-6 lg:grid-cols-[1fr_1fr]">
				<section className="space-y-4">
					<h2 className="text-2xl font-semibold">Rule management</h2>
					<form action={createRuleAction} className="grid gap-4">
						<label className="grid gap-2" htmlFor="engine">
							<span className="text-sm font-medium">Engine</span>
							<select
								className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
								defaultValue={model.ruleFormValues.engine}
								id="engine"
								name="engine"
							>
								{model.ruleCatalog.map((catalog) => (
									<option key={catalog.engine} value={catalog.engine}>
										{formatDatabaseEngine(catalog.engine)}
									</option>
								))}
							</select>
						</label>
						{model.ruleFields.map((field) => (
							<label className="grid gap-2" htmlFor={field.name} key={field.name}>
								<span className="text-sm font-medium">{field.label}</span>
								<input
									className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
									defaultValue={getRuleFieldValue(model, field.name)}
									id={field.name}
									list={field.name === "metric_name" ? "supported-rule-metrics" : undefined}
									name={field.name}
									type={field.type}
								/>
							</label>
						))}
						<datalist id="supported-rule-metrics">
							{model.ruleCatalog.flatMap((catalog) =>
								catalog.metrics.map((metric) => (
									<option
										key={`${catalog.engine}-${metric.metric_name}`}
										value={metric.metric_name}
									/>
								)),
							)}
						</datalist>
						<div className="grid gap-4 md:grid-cols-2">
							<label className="grid gap-2" htmlFor="operator">
								<span className="text-sm font-medium">Operator</span>
								<select
									className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
									defaultValue={model.ruleFormValues.operator}
									id="operator"
									name="operator"
								>
									{RULE_OPERATORS.map((operator) => (
										<option key={operator} value={operator}>
											{operator}
										</option>
									))}
								</select>
							</label>
							<label className="grid gap-2" htmlFor="severity">
								<span className="text-sm font-medium">Severity</span>
								<select
									className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
									defaultValue={model.ruleFormValues.severity}
									id="severity"
									name="severity"
								>
									{RULE_SEVERITIES.map((severity) => (
										<option key={severity} value={severity}>
											{severity}
										</option>
									))}
								</select>
							</label>
						</div>
						<button
							className="rounded-[1rem] bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white"
							type="submit"
						>
							Create rule
						</button>
					</form>
					<div className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4">
						<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
							Supported metrics
						</p>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Rules stay engine-scoped in the current baseline. Availability and gauge metrics are
							supported here; raw counters remain intentionally excluded.
						</p>
						<div className="mt-4 grid gap-4 md:grid-cols-2">
							{model.ruleCatalog.map((catalog) => (
								<div
									className="rounded-[1rem] border border-black/5 bg-white/80 p-4"
									key={catalog.engine}
								>
									<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--muted)]">
										{formatDatabaseEngine(catalog.engine)}
									</p>
									<div className="mt-3 flex flex-wrap gap-2">
										{catalog.metrics.map((metric) => (
											<span
												className="rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-[var(--ink)]"
												key={metric.metric_name}
											>
												{metric.label} · {metric.metric_name}
											</span>
										))}
									</div>
								</div>
							))}
						</div>
					</div>
				</section>
				<section className="space-y-4">
					<h2 className="text-2xl font-semibold">Active rules</h2>
					{model.rules.map((rule) => (
						<div
							className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4"
							key={rule.rule_id}
						>
							<div className="flex flex-wrap items-baseline justify-between gap-2">
								<p className="font-semibold">{rule.name}</p>
								<Link
									className="rounded-[0.6rem] border border-[var(--accent)] bg-white px-3 py-1 text-xs font-semibold text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white"
									href={`/rules/${rule.rule_id}`}
								>
									编辑
								</Link>
							</div>
							<p className="text-sm text-[var(--muted)]">
								{formatDatabaseEngine(rule.engine)} · {rule.metric_name}
							</p>
							<p className="mt-2 text-sm text-[var(--muted)]">
								Scope:{" "}
								{rule.instance_ids.length === 0
									? `all ${formatDatabaseEngine(rule.engine)} instances`
									: rule.instance_ids.join(", ")}
							</p>
							<p className="mt-2 text-xs uppercase tracking-[0.22em] text-[var(--accent)]">
								{rule.severity}
							</p>
						</div>
					))}
				</section>
			</div>
		</AppChrome>
	);
}

function getRuleFieldValue(model: ReturnType<typeof buildOperationsModel>, key: string): string {
	return model.ruleFormValues[key as keyof typeof model.ruleFormValues] ?? "";
}
