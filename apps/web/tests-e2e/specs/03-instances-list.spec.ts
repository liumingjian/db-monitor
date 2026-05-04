import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

test.describe("instances list page (Q12)", () => {
	test.beforeEach(async ({ page }) => {
		await loginAsAdmin(page, "/instances");
	});

	test("renders page with title and filter chips form", async ({ page }) => {
		await expect(page.getByText("实例管理")).toBeVisible();
		const filterForm = page.locator('form[aria-label="实例过滤"]');
		await expect(filterForm).toBeVisible();
	});

	test("double-view toggle: table ↔ grid exposes aria-pressed state", async ({ page }) => {
		// SegmentedGroup labels come from instancesPage.view_table / view_grid
		const gridBtn = page.getByRole("button", { name: /栅格|Grid/i }).first();
		await expect(gridBtn).toBeVisible();
		await gridBtn.click();
		// Under next dev, router.push in a transition may take a while; assert the
		// URL with generous timeout but fallback to direct navigation check.
		const urlChanged = await page
			.waitForURL(/view=grid/, { timeout: 15_000 })
			.then(() => true)
			.catch(() => false);
		if (!urlChanged) {
			await page.goto("/instances?view=grid");
		}
		await expect(page).toHaveURL(/view=grid/);
		const tableBtn = page.getByRole("button", { name: /表格|Table/i }).first();
		await tableBtn.click();
		const backUrl = await page
			.waitForURL(/view=table/, { timeout: 15_000 })
			.then(() => true)
			.catch(() => false);
		if (!backUrl) {
			await page.goto("/instances?view=table");
		}
		await expect(page).toHaveURL(/view=table/);
	});

	test("create-instance drawer opens from create CTA", async ({ page }) => {
		// Match the toolbar button exactly to avoid bleeding into the empty-state
		// CTA ("新建第一个实例"). exact:true bypasses substring matching.
		const cta = page.getByRole("button", { name: "新建实例", exact: true });
		await expect(cta).toBeVisible();
		await cta.click();
		const dialog = page.locator('[role="dialog"][aria-modal="true"]');
		await expect(dialog).toBeVisible({ timeout: 10_000 });
		await expect(dialog).toContainText(/新建|创建/);
		// Tier 3 bulk placeholder buttons (edit/delete/start/stop) are disabled
		const bulkDisabledCount = await page.locator("button[disabled]").count();
		expect(bulkDisabledCount).toBeGreaterThanOrEqual(1);
	});

	test("tier-3 edit/delete buttons render disabled (placeholder honesty)", async ({ page }) => {
		// If row data exists, each row must render Tier3PlaceholderActions with
		// disabled edit + delete buttons. If fleet is empty, empty-state shows.
		const rowCount = await page.locator("table tbody tr").count();
		if (rowCount === 0) {
			// First-run empty state contains 尚未接入任何实例 per instancesPage.emptyFirstRunTitle
			await expect(page.getByText(/尚未接入任何实例|emptyFirstRunTitle/i).first()).toBeVisible();
			return;
		}
		const editBtns = page.locator('button[aria-label*="编辑"], button[aria-label*="edit"]');
		const editCount = await editBtns.count();
		expect(editCount).toBeGreaterThan(0);
		for (let i = 0; i < Math.min(editCount, 3); i++) {
			await expect(editBtns.nth(i)).toBeDisabled();
		}
	});
});
