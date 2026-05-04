import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

test.describe("settings + audit (Q15)", () => {
	test("settings side nav has 6 groups and selecting each changes active panel", async ({
		page,
	}) => {
		await loginAsAdmin(page, "/settings");
		// SettingsSideNav renders label + count inside each button; match the
		// label text only and select the first button containing it.
		const labels = ["通用", "留存策略", "通知", "集成", "高级", "关于"];
		for (const label of labels) {
			const btn = page.locator("nav[aria-label='Settings'] button", { hasText: label }).first();
			await expect(btn).toBeVisible();
			await btn.click();
			await expect(btn).toHaveAttribute("aria-current", "page");
		}
	});

	test("audit feed page renders with header or empty state", async ({ page }) => {
		await loginAsAdmin(page, "/admin/audit");
		await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible();
	});
});
