import { RULE_OPERATORS, RULE_SEVERITIES } from "@db-monitor/ui";
import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	EntitySummary,
	Input,
	Label,
} from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";

import { RulesCatalog } from "../../src/components/rules/rules-catalog";
import { buildRulesCatalogCopy } from "../../src/components/rules/rules-copy";
import { RulesShell } from "../../src/components/rules/rules-shell";
import { createRuleAction } from "../../src/monitoring-actions";
import { buildOperationsModel, formatDatabaseEngine } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

export default async function RulesPage() {
	const session = await requireServerSession("/rules");
	const apiClient = await createServerApiClient();
	const [ruleCatalog, rules] = await Promise.all([
		apiClient.listRuleCatalog(),
		apiClient.listRules(),
	]);
	const model = buildOperationsModel({ ruleCatalog, rules });

	const t = await getTranslations("rulesPage");
	const tCommon = await getTranslations("common");
	const tNav = await getTranslations("nav");
	const tTopbar = await getTranslations("topbar");

	const catalogCopy = buildRulesCatalogCopy(t, tCommon);
	const username = session.displayName ?? session.username ?? tCommon("appName");

	return (
		<RulesShell
			breadcrumbs={[{ href: "/alerts", label: tNav("alert") }, { label: tNav("rules") }]}
			entitySummary={
				<EntitySummary
					badges={[{ label: t("title"), tone: "info" }]}
					subtitle={t("subtitle")}
					title={t("title")}
				/>
			}
			labels={{
				admin: tNav("admin"),
				alert: tNav("alert"),
				commandLabel: tTopbar("commandPalette"),
				notificationLabel: tTopbar("notifications"),
				observe: tNav("observe"),
				operate: tNav("operate"),
				sidebarAlerts: tNav("alerts"),
				sidebarInstances: tNav("instances"),
				sidebarOverview: tNav("overview"),
				sidebarRules: tNav("rules"),
				sidebarSettings: tNav("settings"),
				themeToggleDark: tTopbar("themeToggleDark"),
				themeToggleLight: tTopbar("themeToggleLight"),
			}}
			username={username}
		>
			<div className="space-y-6">
				<RulesCatalog copy={catalogCopy} rules={model.rules} />
				<CreateRuleCard
					catalog={model.ruleCatalog}
					ruleFormValues={model.ruleFormValues}
					ruleFields={model.ruleFields}
					tCreate={t}
					tCommon={tCommon}
				/>
			</div>
		</RulesShell>
	);
}

interface CreateRuleCardProps {
	readonly catalog: ReturnType<typeof buildOperationsModel>["ruleCatalog"];
	readonly ruleFormValues: ReturnType<typeof buildOperationsModel>["ruleFormValues"];
	readonly ruleFields: ReturnType<typeof buildOperationsModel>["ruleFields"];
	readonly tCreate: Awaited<ReturnType<typeof getTranslations>>;
	readonly tCommon: Awaited<ReturnType<typeof getTranslations>>;
}

function CreateRuleCard({ catalog, ruleFormValues, ruleFields, tCreate }: CreateRuleCardProps) {
	return (
		<Card>
			<CardHeader>
				<CardTitle>{tCreate("create.heading")}</CardTitle>
				<CardDescription>{tCreate("create.hintMetric")}</CardDescription>
			</CardHeader>
			<CardContent>
				<form action={createRuleAction} className="grid gap-4 md:grid-cols-2">
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="engine" required>
							{tCreate("create.fieldEngine")}
						</Label>
						<select
							className="h-9 rounded-md border border-border-subtle bg-bg-elevated px-3 text-sm text-fg-primary outline-none focus-visible:ring-2 focus-visible:ring-ring"
							defaultValue={ruleFormValues.engine}
							id="engine"
							name="engine"
						>
							{catalog.map((entry) => (
								<option key={entry.engine} value={entry.engine}>
									{formatDatabaseEngine(entry.engine)}
								</option>
							))}
						</select>
					</div>
					{ruleFields.map((field) => (
						<div className="flex flex-col gap-1.5" key={field.name}>
							<Label htmlFor={field.name}>{field.label}</Label>
							<Input
								defaultValue={readFieldValue(ruleFormValues, field.name)}
								id={field.name}
								list={field.name === "metric_name" ? "supported-rule-metrics" : undefined}
								name={field.name}
								type={field.type}
							/>
						</div>
					))}
					<datalist id="supported-rule-metrics">
						{catalog.flatMap((entry) =>
							entry.metrics.map((metric) => (
								<option key={`${entry.engine}-${metric.metric_name}`} value={metric.metric_name} />
							)),
						)}
					</datalist>
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="operator">{tCreate("create.fieldOperator")}</Label>
						<select
							className="h-9 rounded-md border border-border-subtle bg-bg-elevated px-3 text-sm text-fg-primary outline-none focus-visible:ring-2 focus-visible:ring-ring"
							defaultValue={ruleFormValues.operator}
							id="operator"
							name="operator"
						>
							{RULE_OPERATORS.map((operator) => (
								<option key={operator} value={operator}>
									{operator}
								</option>
							))}
						</select>
					</div>
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="severity">{tCreate("create.fieldSeverity")}</Label>
						<select
							className="h-9 rounded-md border border-border-subtle bg-bg-elevated px-3 text-sm text-fg-primary outline-none focus-visible:ring-2 focus-visible:ring-ring"
							defaultValue={ruleFormValues.severity}
							id="severity"
							name="severity"
						>
							{RULE_SEVERITIES.map((severity) => (
								<option key={severity} value={severity}>
									{severity}
								</option>
							))}
						</select>
					</div>
					<div className="md:col-span-2 flex justify-end">
						<Button type="submit" variant="default">
							{tCreate("create.submit")}
						</Button>
					</div>
				</form>
			</CardContent>
		</Card>
	);
}

function readFieldValue(
	values: ReturnType<typeof buildOperationsModel>["ruleFormValues"],
	key: string,
): string {
	return values[key as keyof typeof values] ?? "";
}
