import type { getTranslations } from "next-intl/server";

import type { EditOverrideDialogCopy } from "./edit-override-dialog";
import type { OverridesPanelCopy } from "./overrides-panel";
import type { RuleAuditCopy } from "./rule-audit-timeline";
import type { RuleDefinitionCopy } from "./rule-definition-panel";
import type { RuleDetailTabsCopy } from "./rule-detail-tabs";
import type { RuleNotificationsCopy } from "./rule-notifications-panel";
import type { RulesCatalogCopy } from "./rules-catalog";

type Translator = Awaited<ReturnType<typeof getTranslations>>;

export function buildRulesCatalogCopy(t: Translator, tCommon: Translator): RulesCatalogCopy {
	return {
		batchClearSelection: t("catalog.batchClearSelection"),
		batchDisable: t("catalog.batchDisable"),
		batchEnable: t("catalog.batchEnable"),
		columnActions: t("catalog.columnActions"),
		columnEnabled: t("catalog.columnEnabled"),
		columnEngine: t("catalog.columnEngine"),
		columnMetric: t("catalog.columnMetric"),
		columnName: t("catalog.columnName"),
		columnOverrides: t("catalog.columnOverrides"),
		columnSeverity: t("catalog.columnSeverity"),
		columnThreshold: t("catalog.columnThreshold"),
		empty: t("catalog.empty"),
		enabledOff: tCommon("disabled"),
		enabledOn: tCommon("enabled"),
		filterAllEnabled: t("catalog.filterAllEnabled"),
		filterAllEngines: t("catalog.filterAllEngines"),
		filterAllSeverities: t("catalog.filterAllSeverities"),
		filterEnabled: t("catalog.filterEnabled"),
		filterEngine: t("catalog.filterEngine"),
		filterSeverity: t("catalog.filterSeverity"),
		heading: t("catalog.heading"),
		searchPlaceholder: t("catalog.searchPlaceholder"),
		viewDetail: t("catalog.viewDetail"),
	};
}

export function buildRuleDefinitionCopy(t: Translator, tCommon: Translator): RuleDefinitionCopy {
	return {
		description: t("tips"),
		enabledOff: tCommon("disabled"),
		enabledOn: tCommon("enabled"),
		heading: t("detail.tabDefinition"),
		metaCreated: t("detail.metaCreated"),
		metaDefaultThreshold: t("detail.metaDefaultThreshold"),
		metaEnabled: t("detail.metaEnabled"),
		metaOperator: t("detail.metaOperator"),
		metaOverridesCount: t("detail.metaOverridesCount"),
		metaScope: t("detail.metaScope"),
		metaSeverity: t("detail.metaSeverity"),
	};
}

export function buildRuleAuditCopy(t: Translator): RuleAuditCopy {
	return {
		created: t("audit.created"),
		description: t("audit.description"),
		heading: t("audit.heading"),
		placeholderEntry: t("audit.placeholderEntry"),
	};
}

export function buildRuleNotificationsCopy(t: Translator): RuleNotificationsCopy {
	return {
		description: t("notifications.description"),
		emptyChannels: t("notifications.emptyChannels"),
		heading: t("notifications.heading"),
		placeholder: t("notifications.placeholder"),
	};
}

export function buildRuleDetailTabsCopy(t: Translator): RuleDetailTabsCopy {
	return {
		audit: t("detail.tabAudit"),
		definition: t("detail.tabDefinition"),
		notifications: t("detail.tabNotifications"),
		overrides: t("detail.tabOverrides"),
	};
}

export function buildOverridesPanelCopy(t: Translator): OverridesPanelCopy {
	return {
		addOverride: t("overrides.addOverride"),
		columnActions: t("overrides.columnActions"),
		columnEnabled: t("overrides.columnEnabled"),
		columnInstance: t("overrides.columnInstance"),
		columnThreshold: t("overrides.columnThreshold"),
		delete: t("overrides.delete"),
		dialog: buildEditOverrideDialogCopy(t),
		editOverride: t("overrides.editOverride"),
		empty: t("overrides.empty"),
		errorSave: (message) => t("detail.errorSave", { message }),
		heading: t("overrides.heading"),
		inheritedThreshold: t("overrides.thresholdPlaceholder"),
		save: t("overrides.save"),
		savedBanner: t("detail.savedBanner"),
		saving: t("overrides.saving"),
		stateInherit: t("overrides.stateInherit"),
		stateOff: t("overrides.stateOff"),
		stateOn: t("overrides.stateOn"),
		tips: t("detail.tips"),
	};
}

function buildEditOverrideDialogCopy(t: Translator): EditOverrideDialogCopy {
	return {
		cancel: t("overrides.dialogCancel"),
		description: t("overrides.dialogDescription"),
		enabledLabel: t("overrides.columnEnabled"),
		inheritedFromRule: (threshold) => t("overrides.inheritedFromRule", { threshold }),
		instanceLabel: t("overrides.columnInstance"),
		instancePlaceholder: t("overrides.instancePlaceholder"),
		save: t("overrides.dialogSave"),
		stateInherit: t("overrides.stateInherit"),
		stateInheritHelp: t("overrides.stateInheritHelp"),
		stateOff: t("overrides.stateOff"),
		stateOffHelp: t("overrides.stateOffHelp"),
		stateOn: t("overrides.stateOn"),
		stateOnHelp: t("overrides.stateOnHelp"),
		thresholdLabel: t("overrides.thresholdLabel"),
		thresholdPlaceholder: t("overrides.thresholdPlaceholder"),
		title: t("overrides.dialogTitle"),
	};
}
