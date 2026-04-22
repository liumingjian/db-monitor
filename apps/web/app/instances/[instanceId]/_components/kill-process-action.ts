"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";

import {
	KILL_ERROR_FALLBACK,
	type KillProcessErrorCode,
	mapKillStatusToCode,
} from "../../../../src/processlist-ui";
import { getServerApiBaseUrl } from "../../../../src/server-api";

export interface KillProcessResultOk {
	readonly ok: true;
	readonly checkedAt: string;
}

export interface KillProcessResultErr {
	readonly ok: false;
	readonly code: KillProcessErrorCode;
	readonly message: string;
}

export type KillProcessResult = KillProcessResultOk | KillProcessResultErr;

export async function killProcessAction(
	_previousState: KillProcessResult | null,
	formData: FormData,
): Promise<KillProcessResult> {
	const parsed = parseFormInput(formData);
	if (parsed === null) {
		return buildError("invalid_input");
	}
	const response = await sendKillRequest(parsed);
	if (response.ok) {
		revalidatePath(`/instances/${parsed.instanceId}/processes`);
		const body = (await response.json()) as { readonly checked_at: string };
		return { checkedAt: body.checked_at, ok: true };
	}
	const code = mapKillStatusToCode(response.status);
	const detail = await safeReadDetail(response);
	return buildError(code, detail);
}

interface KillRequestInput {
	readonly instanceId: string;
	readonly processId: number;
	readonly reason: string;
}

function parseFormInput(formData: FormData): KillRequestInput | null {
	const instanceId = readString(formData, "instance_id");
	const processIdRaw = readString(formData, "process_id");
	const reason = readString(formData, "reason");
	if (instanceId === null || processIdRaw === null || reason === null) {
		return null;
	}
	const processId = Number.parseInt(processIdRaw, 10);
	if (!Number.isFinite(processId) || processId < 0) {
		return null;
	}
	return { instanceId, processId, reason };
}

async function sendKillRequest(input: KillRequestInput): Promise<Response> {
	const cookieStore = await cookies();
	const cookieHeader = cookieStore
		.getAll()
		.map((cookie) => `${cookie.name}=${cookie.value}`)
		.join("; ");
	const baseUrl = getServerApiBaseUrl().replace(/\/$/, "");
	const url = `${baseUrl}/instances/${input.instanceId}/processlist/${input.processId}/kill`;
	return fetch(url, {
		body: JSON.stringify({ reason: input.reason }),
		cache: "no-store",
		headers: {
			"Content-Type": "application/json",
			...(cookieHeader.length === 0 ? {} : { cookie: cookieHeader }),
		},
		method: "POST",
	});
}

async function safeReadDetail(response: Response): Promise<string | null> {
	try {
		const body = (await response.json()) as { readonly detail?: string };
		return typeof body.detail === "string" && body.detail.length > 0 ? body.detail : null;
	} catch {
		return null;
	}
}

function buildError(code: KillProcessErrorCode, detail: string | null = null): KillProcessResultErr {
	return {
		code,
		message: detail ?? KILL_ERROR_FALLBACK[code],
		ok: false,
	};
}

function readString(formData: FormData, key: string): string | null {
	const value = formData.get(key);
	if (typeof value !== "string") {
		return null;
	}
	const trimmed = value.trim();
	return trimmed.length === 0 ? null : trimmed;
}
