"use server";

import { revalidatePath } from "next/cache";

import type {
	AlertRuleResponse,
	RuleOverrideRequest,
	UpdateAlertRuleRequest,
} from "@db-monitor/api-client";

import { createServerApiClient } from "../../../src/server-api";

export interface SetRulesEnabledInput {
	readonly ruleIds: readonly string[];
	readonly enabled: boolean;
}

export interface BatchRulesOk {
	readonly ok: true;
	readonly updated: number;
}

export interface BatchRulesErr {
	readonly ok: false;
	readonly message: string;
}

export type BatchRulesResult = BatchRulesOk | BatchRulesErr;

export async function setRulesEnabledAction(
	input: SetRulesEnabledInput,
): Promise<BatchRulesResult> {
	if (input.ruleIds.length === 0) {
		return { message: "no rules selected", ok: false };
	}
	try {
		const apiClient = await createServerApiClient();
		const updatedRules = await Promise.all(
			input.ruleIds.map(async (ruleId) => {
				const rule = await apiClient.getRule(ruleId);
				const payload = buildEnabledUpdatePayload(rule, input.enabled);
				await apiClient.updateRule(ruleId, payload);
			}),
		);
		revalidatePath("/rules");
		for (const ruleId of input.ruleIds) {
			revalidatePath(`/rules/${ruleId}`);
		}
		return { ok: true, updated: updatedRules.length };
	} catch (error) {
		return { message: toErrorMessage(error), ok: false };
	}
}

function buildEnabledUpdatePayload(
	rule: AlertRuleResponse,
	enabled: boolean,
): UpdateAlertRuleRequest {
	return {
		enabled,
		engine: rule.engine,
		instance_ids: rule.instance_ids,
		metric_name: rule.metric_name,
		name: rule.name,
		operator: rule.operator as UpdateAlertRuleRequest["operator"],
		overrides: rule.overrides.map(toOverrideRequest),
		severity: rule.severity as UpdateAlertRuleRequest["severity"],
		threshold: rule.threshold,
	};
}

function toOverrideRequest(override: AlertRuleResponse["overrides"][number]): RuleOverrideRequest {
	return {
		enabled: override.enabled,
		instance_id: override.instance_id,
		threshold: override.threshold,
	};
}

function toErrorMessage(error: unknown): string {
	if (error instanceof Error) {
		return error.message;
	}
	return "batch update failed";
}
