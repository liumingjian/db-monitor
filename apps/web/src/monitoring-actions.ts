"use server";

import type { CreateAlertRuleRequest, CreateInstanceRequest } from "@db-monitor/api-client";
import { RULE_OPERATORS, RULE_SEVERITIES } from "@db-monitor/ui";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { createServerApiClient } from "./server-api";

export async function createInstanceAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const instance = await apiClient.createInstance(buildInstancePayload(formData));
	revalidatePath("/instances");
	revalidatePath("/overview");
	redirect(`/instances/${instance.instance_id}`);
}

export async function createRuleAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	await apiClient.createRule(buildRulePayload(formData));
	revalidatePath("/rules");
	revalidatePath("/alerts");
	redirect("/rules");
}

export async function updateSettingAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const key = readTextField(formData, "key");
	const value = readTextField(formData, "value");
	await apiClient.updateSetting(key, value);
	revalidatePath("/settings");
	redirect("/settings");
}

export async function updateUserRolesAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const userId = readTextField(formData, "user_id");
	await apiClient.updateUserRoles(userId, {
		roles: readTextValues(formData, "roles"),
	});
	revalidatePath("/settings");
	redirect("/settings");
}

export async function acknowledgeAlertAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const alertId = readTextField(formData, "alert_id");
	await apiClient.acknowledgeAlert(alertId);
	revalidateAlertPaths(alertId);
	redirect(`/alerts/${alertId}`);
}

export async function assignAlertOwnerAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const alertId = readTextField(formData, "alert_id");
	await apiClient.assignAlertOwner(alertId, {
		owner_user_id: readTextField(formData, "owner_user_id"),
	});
	revalidateAlertPaths(alertId);
	redirect(`/alerts/${alertId}`);
}

export async function addAlertNoteAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const alertId = readTextField(formData, "alert_id");
	await apiClient.addAlertNote(alertId, {
		note: readTextField(formData, "note"),
	});
	revalidateAlertPaths(alertId);
	redirect(`/alerts/${alertId}`);
}

function buildInstancePayload(formData: FormData): CreateInstanceRequest {
	const engine = parseInstanceEngine(formData);
	return {
		connection: {
			database: readTextField(formData, "database"),
			host: readTextField(formData, "host"),
			password: readTextField(formData, "password"),
			port: Number.parseInt(readTextField(formData, "port"), 10),
			username: readTextField(formData, "username"),
		},
		engine,
		environment: readTextField(formData, "environment"),
		labels: parseCsvField(formData, "labels"),
		name: readTextField(formData, "name"),
	};
}

function buildRulePayload(formData: FormData): CreateAlertRuleRequest {
	return {
		enabled: true,
		engine: parseRuleEngine(formData),
		instance_ids: parseCsvField(formData, "instance_ids"),
		metric_name: readTextField(formData, "metric_name"),
		name: readTextField(formData, "name"),
		operator: parseChoice(formData, "operator", RULE_OPERATORS),
		severity: parseChoice(formData, "severity", RULE_SEVERITIES),
		threshold: Number.parseFloat(readTextField(formData, "threshold")),
	};
}

function parseChoice<T extends string>(formData: FormData, key: string, choices: readonly T[]): T {
	const value = readTextField(formData, key);
	if (choices.includes(value as T)) {
		return value as T;
	}
	throw new Error(`Unsupported value for ${key}: ${value}`);
}

function parseRuleEngine(formData: FormData): "mysql" | "oracle" {
	const value = formData.get("engine");
	if (value === "oracle") {
		return "oracle";
	}
	return "mysql";
}

function parseInstanceEngine(formData: FormData): "mysql" | "oracle" {
	const value = formData.get("engine");
	if (value === "oracle") {
		return "oracle";
	}
	return "mysql";
}

function parseCsvField(formData: FormData, key: string): string[] {
	return readTextField(formData, key)
		.split(",")
		.map((entry) => entry.trim())
		.filter((entry) => entry.length > 0);
}

function readTextField(formData: FormData, key: string): string {
	const value = formData.get(key);
	if (typeof value !== "string" || value.trim().length === 0) {
		throw new Error(`Missing form field: ${key}`);
	}
	return value.trim();
}

function readTextValues(formData: FormData, key: string): string[] {
	return formData
		.getAll(key)
		.flatMap((value) => (typeof value === "string" ? [value.trim()] : []))
		.filter((value) => value.length > 0);
}

function revalidateAlertPaths(alertId: string): void {
	revalidatePath("/alerts");
	revalidatePath(`/alerts/${alertId}`);
}
