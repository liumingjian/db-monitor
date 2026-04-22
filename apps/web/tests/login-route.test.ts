import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "../app/api/login/route";

describe("login route", () => {
	afterEach(() => {
		vi.restoreAllMocks();
	});

	it("returns a see-other redirect with the propagated session cookie", async () => {
		vi.stubGlobal(
			"fetch",
			vi.fn().mockResolvedValue(
				new Response(
					JSON.stringify({
						display_name: "Platform Admin",
						permissions: ["*"],
						roles: ["admin"],
						user_id: "user-admin",
						username: "admin",
					}),
					{
						headers: {
							"content-type": "application/json",
							"set-cookie": "dbmon_session=session-123; HttpOnly; Path=/; SameSite=Lax",
						},
						status: 200,
					},
				),
			),
		);

		const formData = new FormData();
		formData.set("username", "admin");
		formData.set("password", "admin-password");
		formData.set("next", "/overview");

		const request = new Request("http://127.0.0.1:38101/api/login", {
			body: formData,
			method: "POST",
		});

		const response = await POST(request);

		expect(response.status).toBe(303);
		expect(response.headers.get("location")).toBe("/overview");
		expect(response.headers.get("set-cookie")).toContain("dbmon_session=session-123");
	});
});
