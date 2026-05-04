import { Badge, Button, EntitySummary } from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";
import Link from "next/link";

import { OverridesPanel } from "../../../src/components/rules/overrides-panel";
import { RuleAuditTimeline } from "../../../src/components/rules/rule-audit-timeline";
import { RuleDefinitionPanel } from "../../../src/components/rules/rule-definition-panel";
import { RuleDetailTabs } from "../../../src/components/rules/rule-detail-tabs";
import { formatScopeSummary } from "../../../src/components/rules/rule-list-models";
import { RuleNotificationsPanel } from "../../../src/components/rules/rule-notifications-panel";
import {
	buildOverridesPanelCopy,
	buildRuleAuditCopy,
	buildRuleDefinitionCopy,
	buildRuleDetailTabsCopy,
	buildRuleNotificationsCopy,
} from "../../../src/components/rules/rules-copy";
import { RulesShell } from "../../../src/components/rules/rules-shell";
import { toDraftRows } from "../../../src/rule-overrides-ui";
import { createServerApiClient, requireServerSession } from "../../../src/server-api";

import { updateRuleAction } from "./_components/update-rule-action";

interface RuleDetailPageProps {
	readonly params: Promise<{ readonly ruleId: string }>;
	readonly searchParams: Promise<{ readonly saved?: string }>;
}

export default async function RuleDetailPage({ params, searchParams }: RuleDetailPageProps) {
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

	const t = await getTranslations("rulesPage");
	const tCommon = await getTranslations("common");
	const tNav = await getTranslations("nav");
	const tTopbar = await getTranslations("topbar");

	const tabsCopy = buildRuleDetailTabsCopy(t);
	const definitionCopy = buildRuleDefinitionCopy(t, tCommon);
	const overridesCopy = buildOverridesPanelCopy(t);
	const notificationsCopy = buildRuleNotificationsCopy(t);
	const auditCopy = buildRuleAuditCopy(t);
	const username = session.displayName ?? session.username ?? tCommon("appName");

	return (
		<RulesShell
			breadcrumbs={[
				{ href: "/alerts", label: tNav("alert") },
				{ href: "/rules", label: tNav("rules") },
				{ label: rule.name },
			]}
			entitySummary={
				<EntitySummary
					actions={
						<Button asChild size="sm" variant="outline">
							<Link href="/rules">{t("detail.back")}</Link>
						</Button>
					}
					badges={[
						{
							label: rule.severity,
							tone: rule.severity === "critical" ? "critical" : "warning",
						},
						{ label: rule.engine.toUpperCase(), tone: "info" },
						{
							label: rule.enabled ? tCommon("enabled") : tCommon("disabled"),
							tone: rule.enabled ? "ok" : "info",
						},
					]}
					subtitle={`${rule.metric_name} · ${formatScopeSummary(rule)}`}
					title={rule.name}
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
			<div className="space-y-4">
				{saved === "1" ? (
					<Badge className="bg-sev-ok/15 text-sev-ok" variant="outline">
						{t("detail.savedBanner")}
					</Badge>
				) : null}
				<p className="text-sm text-fg-muted">{t("detail.tips")}</p>
				<RuleDetailTabs
					audit={<RuleAuditTimeline copy={auditCopy} rule={rule} />}
					copy={tabsCopy}
					definition={<RuleDefinitionPanel copy={definitionCopy} rule={rule} />}
					notifications={<RuleNotificationsPanel copy={notificationsCopy} />}
					overrides={
						<OverridesPanel
							action={updateRuleAction}
							copy={overridesCopy}
							initialRows={initialRows}
							instances={engineInstances.map((instance) => ({
								id: instance.instance_id,
								label: `${instance.name} (${instance.instance_id})`,
							}))}
							ruleDefaultThreshold={rule.threshold}
							ruleId={rule.rule_id}
						/>
					}
					rule={rule}
				/>
			</div>
		</RulesShell>
	);
}
