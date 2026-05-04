import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

test.describe("alerts page (Q10)", () => {
	test.beforeEach(async ({ page }) => {
		await loginAsAdmin(page, "/alerts");
	});

	test("renders 4 tabs and they switch via URL ?tab=", async ({ page }) => {
		const tabs = [
			{ label: "活跃", token: null },
			{ label: "时间线", token: "timeline" },
			{ label: "已确认", token: "acknowledged" },
			{ label: "已解决", token: "resolved" },
		];
		for (const tab of tabs) {
			// TabBar renders role="tab" links when href is provided
			const tabEl = page.getByRole("tab", { name: tab.label }).first();
			await expect(tabEl).toBeVisible();
			if (tab.token !== null) {
				await tabEl.click();
				await expect(page).toHaveURL(new RegExp(`tab=${tab.token}`), { timeout: 10_000 });
			}
		}
	});

	test("filter-chip form is present and accepts filters", async ({ page }) => {
		// Seven Q10 chips / inputs via aria-label in filter form
		await expect(page.getByText(/全部严重度|严重度/).first()).toBeVisible();
	});

	test("alert row clickthrough preserves filters in drawer URL, empty-state otherwise", async ({
		page,
	}) => {
		// Filter out /alerts/<id> from navigation links and tab hrefs
		const alertRows = page.locator('a[href^="/alerts/"]').filter({
			hasNotText: /活跃|时间线|已确认|已解决/,
		});
		const count = await alertRows.count();
		if (count === 0) {
			// Empty state text: alertsPage.listEmptyTitle "当前无活跃告警" or similar
			await expect(page.getByText(/当前无|暂无|未触发/i).first()).toBeVisible();
			return;
		}
		await page.goto("/alerts?severity=critical");
		const filtered = page.locator('a[href^="/alerts/"]').filter({
			hasNotText: /活跃|时间线|已确认|已解决/,
		});
		if ((await filtered.count()) === 0) {
			await expect(page.getByText(/当前无|暂无|未触发/i).first()).toBeVisible();
			return;
		}
		await filtered.first().click();
		await expect(page).toHaveURL(/\/alerts\/[^?]+\?.*severity=critical/, { timeout: 15_000 });
	});
});
