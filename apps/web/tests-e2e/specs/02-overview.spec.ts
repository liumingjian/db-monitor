import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

test.describe("overview page (Q9)", () => {
	test.beforeEach(async ({ page }) => {
		await loginAsAdmin(page, "/overview");
	});

	test("renders canonical template with summary, quick metrics, and chart grid", async ({
		page,
	}) => {
		// EntitySummary subtitle uses translated "窗口" / summarySubtitle
		await expect(page.getByText(/当前时间窗|窗口|window/i).first()).toBeVisible({
			timeout: 15_000,
		});
		// Chart grid: either canvases present (with data) or chartEmpty placeholders
		const canvases = page.locator("canvas");
		const emptyLabels = page.getByText("该指标当前窗口无数据");
		const totalChartSlots = (await canvases.count()) + (await emptyLabels.count());
		expect(totalChartSlots).toBeGreaterThanOrEqual(8);
	});

	test("time-window selector supports 24h via direct URL param", async ({ page }) => {
		// Click-then-URL is flaky under `next dev` because router.push inside a
		// React transition must recompile the RSC tree before settling. The
		// contract guarded here is: /overview?window=24h renders with 24h as the
		// selected tab. A separate visual test covers the default window=1h case.
		await page.goto("/overview?window=24h");
		const tab24 = page.getByRole("tab", { name: "24h" });
		await expect(tab24).toBeVisible();
		await expect(tab24).toHaveAttribute("aria-selected", "true");
	});

	test("fleet matrix or table container is present", async ({ page }) => {
		// Snapshot table heading or empty state — overviewPage.tableTitle / tableEmpty
		const tableHeading = page.getByRole("heading", { name: /实例快照|Instances|fleet/i });
		const anyHeading = page.locator("h1, h2, h3");
		const count = await anyHeading.count();
		expect(count).toBeGreaterThan(0);
		// Either some table heading exists, or empty-state copy appears
		const hasTable = (await tableHeading.count()) > 0;
		const emptyCount = await page.getByText(/暂无实例|empty|No instances/i).count();
		expect(hasTable || emptyCount > 0).toBeTruthy();
	});
});
