"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import {
	OverrideValidationError,
	type OverrideDraftRow,
	buildUpdateRulePayload,
	parseEnabledTriState,
} from "../../../../src/rule-overrides-ui";
import { createServerApiClient } from "../../../../src/server-api";

export interface UpdateRuleOk {
	readonly ok: true;
	readonly ruleId: string;
}

export interface UpdateRuleErr {
	readonly ok: false;
	readonly message: string;
}

export type UpdateRuleResult = UpdateRuleOk | UpdateRuleErr;

export async function updateRuleAction(
	_previousState: UpdateRuleResult | null,
	formData: FormData,
): Promise<UpdateRuleResult> {
	const prepared = await prepareUpdate(formData);
	if (!prepared.ok) {
		return prepared;
	}
	revalidatePath("/rules");
	revalidatePath(`/rules/${prepared.ruleId}`);
	redirect(`/rules/${prepared.ruleId}?saved=1`);
}

async function prepareUpdate(formData: FormData): Promise<UpdateRuleResult> {
	try {
		const ruleId = readRuleId(formData);
		const rows = readOverrideRows(formData);
		const apiClient = await createServerApiClient();
		const rule = await apiClient.getRule(ruleId);
		const payload = buildUpdateRulePayload({ rows, rule });
		await apiClient.updateRule(ruleId, payload);
		return { ok: true, ruleId };
	} catch (error) {
		return { message: toErrorMessage(error), ok: false };
	}
}

function readRuleId(formData: FormData): string {
	const value = formData.get("rule_id");
	if (typeof value !== "string" || value.trim().length === 0) {
		throw new OverrideValidationError("缺少 rule_id");
	}
	return value.trim();
}

function readOverrideRows(formData: FormData): readonly OverrideDraftRow[] {
	const clientIds = formData.getAll("override_client_id");
	return clientIds
		.filter((value): value is string => typeof value === "string")
		.map((clientId) => buildRow(formData, clientId));
}

function buildRow(formData: FormData, clientId: string): OverrideDraftRow {
	const instanceId = readText(formData, `override_instance_id__${clientId}`);
	if (instanceId.length === 0) {
		throw new OverrideValidationError("override 行未选择实例");
	}
	return {
		clientId,
		enabled: parseEnabledTriState(readText(formData, `override_enabled__${clientId}`)),
		instanceId,
		threshold: readText(formData, `override_threshold__${clientId}`),
	};
}

function readText(formData: FormData, key: string): string {
	const value = formData.get(key);
	return typeof value === "string" ? value.trim() : "";
}

function toErrorMessage(error: unknown): string {
	if (error instanceof OverrideValidationError) {
		return error.message;
	}
	if (error instanceof Error) {
		return error.message;
	}
	return "保存失败：未知错误";
}
