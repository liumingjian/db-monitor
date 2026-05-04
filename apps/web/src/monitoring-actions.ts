"use server";

import type { CreateAlertRuleRequest, CreateInstanceRequest } from "@db-monitor/api-client";
import { RULE_OPERATORS, RULE_SEVERITIES } from "@db-monitor/ui";
import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { createServerApiClient, getServerApiBaseUrl } from "./server-api";

const INSTANCE_ID_PATTERN = /^[A-Za-z0-9_\-]+$/;

export async function createInstanceAction(formData: FormData): Promise<void> {
	const apiClient = await createServerApiClient();
	const instance = await apiClient.createInstance(buildInstancePayload(formData));
	revalidatePath("/instances");
	revalidatePath("/overview");
	redirect(`/instances/${instance.instance_id}`);
}

/**
 * 重验证实例连接。
 *
 * 后端端点 `POST /control/instances/{id}/validate` 已存在（router.py L172），但
 * `@db-monitor/api-client` 尚未暴露方法，而该 package 在 Slice 1.5 写作用域内为只读。
 * 因此这里直接通过 `fetch` + cookie 转发调用，保持端到端的真实链路；失败抛错由
 * Next.js server-action 边界负责显示，**不**进行 silent fallback。
 */
export async function validateInstanceAction(formData: FormData): Promise<void> {
	const instanceId = readTextField(formData, "instance_id");
	if (!INSTANCE_ID_PATTERN.test(instanceId)) {
		throw new Error(`Invalid instance_id: ${instanceId}`);
	}
	const cookieHeader = await buildForwardedCookieHeader();
	const response = await fetch(
		`${getServerApiBaseUrl()}/control/instances/${encodeURIComponent(instanceId)}/validate`,
		{
			cache: "no-store",
			headers: {
				"Content-Type": "application/json",
				...(cookieHeader === null ? {} : { cookie: cookieHeader }),
			},
			method: "POST",
		},
	);
	if (!response.ok) {
		const detail = await safeReadText(response);
		throw new Error(
			`Revalidate failed (HTTP ${response.status}): ${detail.length === 0 ? response.statusText : detail}`,
		);
	}
	revalidatePath("/instances");
	revalidatePath(`/instances/${instanceId}`);
}

async function buildForwardedCookieHeader(): Promise<string | null> {
	const store = await cookies();
	const entries = store
		.getAll()
		.map((cookie) => `${cookie.name}=${cookie.value}`)
		.join("; ");
	return entries.length === 0 ? null : entries;
}

async function safeReadText(response: Response): Promise<string> {
	try {
		return (await response.text()).trim();
	} catch {
		return "";
	}
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
