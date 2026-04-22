import { NextResponse } from "next/server";

import { getServerApiBaseUrl } from "../../../src/server-api";

const SESSION_COOKIE_NAME = "dbmon_session";

export async function POST(request: Request): Promise<Response> {
	const formData = await request.formData();
	const response = await fetch(`${getServerApiBaseUrl()}/auth/login`, {
		body: JSON.stringify({
			password: readTextField(formData, "password"),
			username: readTextField(formData, "username"),
		}),
		cache: "no-store",
		headers: { "Content-Type": "application/json" },
		method: "POST",
	});
	if (!response.ok) {
		throw new Error(await response.text());
	}
	const cookieValue = parseSessionCookie(response.headers.get("set-cookie"));
	if (cookieValue === null) {
		throw new Error("Backend login did not return the db monitor session cookie.");
	}
	const redirectTarget = readOptionalTextField(formData, "next") ?? "/overview";
	const redirectResponse = new NextResponse(null, {
		headers: { location: redirectTarget },
		status: 303,
	});
	redirectResponse.cookies.set(SESSION_COOKIE_NAME, cookieValue, {
		httpOnly: true,
		path: "/",
		sameSite: "lax",
	});
	return redirectResponse;
}

function parseSessionCookie(setCookieHeader: string | null): string | null {
	if (setCookieHeader === null) {
		return null;
	}
	const firstSegment = setCookieHeader.split(";", 1)[0];
	const separatorIndex = firstSegment.indexOf("=");
	if (separatorIndex < 0) {
		return null;
	}
	return firstSegment.slice(separatorIndex + 1);
}

function readOptionalTextField(formData: FormData, key: string): string | null {
	const value = formData.get(key);
	return typeof value === "string" && value.trim().length > 0 ? value.trim() : null;
}

function readTextField(formData: FormData, key: string): string {
	const value = formData.get(key);
	if (typeof value !== "string" || value.trim().length === 0) {
		throw new Error(`Missing form field: ${key}`);
	}
	return value.trim();
}
