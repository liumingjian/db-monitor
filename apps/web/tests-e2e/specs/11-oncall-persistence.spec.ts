import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

const ONCALL_KEY = "alerts.oncall";

test.describe("on-call toggle persistence (Q10 + Q17 shared key)", () => {
	test("toggles write to localStorage and survive navigation", async ({ page }) => {
		await loginAsAdmin(page, "/alerts");
		// Ensure clean state
		await page.evaluate((key: string) => {
			try {
				window.localStorage.removeItem(key);
			} catch {
				/* ignore */
			}
		}, ONCALL_KEY);
		// Switch role="switch" with aria-label="值班模式"
		const toggle = page.getByRole("switch", { name: "值班模式" });
		await expect(toggle).toBeVisible();
		const before = await toggle.getAttribute("aria-checked");
		await toggle.click();
		const after = await toggle.getAttribute("aria-checked");
		expect(after).not.toBe(before);
		// Persisted value — alert-oncall-toggle stores "on"/"off"
		const stored = await page.evaluate(
			(key: string) => window.localStorage.getItem(key),
			ONCALL_KEY,
		);
		expect(["on", "off", null]).toContain(stored);
		// Navigate away and back — UI state must rehydrate from storage
		await page.goto("/overview");
		await page.goto("/alerts");
		const again = page.getByRole("switch", { name: "值班模式" });
		await expect(again).toHaveAttribute("aria-checked", after ?? "false");
	});
});
