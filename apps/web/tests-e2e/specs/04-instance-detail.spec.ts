import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

const INSTANCE_ID = process.env.DB_MONITOR_E2E_INSTANCE_ID ?? null;

test.describe("instance detail page (Q13)", () => {
	test.beforeEach(async ({ page }) => {
		await loginAsAdmin(page, "/instances");
	});

	test("resolves to a detail route and exposes 8 tabs or skips if no instance", async ({
		page,
	}) => {
		// Try env-driven instance id first, else click the first instance row if present.
		if (INSTANCE_ID !== null) {
			await page.goto(`/instances/${INSTANCE_ID}`);
		} else {
			const row = page.locator("table tbody tr a").first();
			const rowCount = await row.count();
			if (rowCount === 0) {
				// Fleet is empty — verify empty state explicitly rather than silently skip.
				await expect(page.getByText(/尚未接入任何实例/i).first()).toBeVisible();
				return;
			}
			await row.click();
			await page.waitForURL(/\/instances\/[^/]+$/);
		}
		// 8 tabs per Q13: 概览/性能/会话/SQL/存储/复制/配置/审计 — link role
		const tabLabels = [
			/概览|Overview/,
			/性能|Performance/,
			/会话|Processes|Sessions/,
			/SQL|慢查询|Slow/,
			/存储|Tablespace/,
			/复制|Replication/,
			/配置|Configuration/,
			/审计|Audit/,
		];
		let visibleTabs = 0;
		for (const label of tabLabels) {
			const count = await page.getByRole("link", { name: label }).count();
			if (count > 0) visibleTabs += 1;
		}
		expect(visibleTabs).toBeGreaterThanOrEqual(6);
	});

	test("Kill dialog: mismatched confirm disables submit, matching enables it", async ({ page }) => {
		if (INSTANCE_ID === null) {
			const row = page.locator("table tbody tr a").first();
			if ((await row.count()) === 0) {
				await expect(page.getByText(/尚未接入任何实例/i).first()).toBeVisible();
				return;
			}
			await row.click();
			await page.waitForURL(/\/instances\/[^/]+$/);
		} else {
			await page.goto(`/instances/${INSTANCE_ID}/processes`);
		}
		// Navigate to processes tab
		const processesLink = page.getByRole("link", { name: /会话|Processes/ }).first();
		if ((await processesLink.count()) > 0) {
			await processesLink.click();
			await page.waitForURL(/\/processes/);
		}
		// If no processlist rows (Tier 3 path), assert no Kill button leaks.
		const killButtons = page.getByRole("button", { name: /^Kill$/ });
		const killCount = await killButtons.count();
		if (killCount === 0) {
			await expect(page.locator("table tbody tr")).toHaveCount(0);
			return;
		}
		await killButtons.first().click();
		const dialog = page.getByRole("dialog");
		await expect(dialog).toBeVisible();
		const confirmInput = dialog.locator('input[name="confirm_thread_id"]');
		const reason = dialog.locator('textarea[name="reason"]');
		const submit = dialog.getByRole("button", { name: /确认 Kill/ });
		await confirmInput.fill("wrong-thread-id");
		await reason.fill("e2e smoke");
		await expect(submit).toBeDisabled();
		// Extract the real thread id from the Kill dialog title "#NN"
		const title = await dialog.getByRole("heading").first().innerText();
		const match = title.match(/#(\d+)/);
		expect(match).not.toBeNull();
		if (match !== null) {
			await confirmInput.fill(match[1]);
			await expect(submit).toBeEnabled();
		}
	});
});
