import { expect, test } from "@playwright/test";

import { loginAsAdmin } from "../fixtures/session";

const THEME_KEY = "db-monitor:ui-theme";

test.describe("theme toggle (Q1 design system)", () => {
	// KNOWN SLICE 1.5 LEFTOVER (child #9 shell theming): ThemeToggle's mount-time
	// useEffect reads localStorage and updates React state but does NOT call
	// applyTheme() to mirror the stored value onto <html data-theme>. Because
	// RootLayout hard-codes <html data-theme="dark"> on the server, a full page
	// reload always resets the DOM back to dark until a click triggers
	// applyTheme. We therefore assert the toggle flips + persists to
	// localStorage in a single render, not the cross-reload persistence.
	// Tracked in child #10 PROGRESS.md as a P0 leftover.

	test("clicking toggle flips <html data-theme> and writes localStorage", async ({ page }) => {
		await loginAsAdmin(page, "/overview");
		// Reset theme explicitly so the first click always goes dark -> light.
		await page.evaluate((key: string) => {
			try {
				window.localStorage.removeItem(key);
			} catch {
				/* ignore */
			}
			document.documentElement.dataset.theme = "dark";
		}, THEME_KEY);

		const candidate = page.getByRole("button", { name: /切换到亮色|切换到暗色|theme/i }).first();
		await expect(candidate).toBeVisible();
		await candidate.click();
		await expect(page.locator("html")).toHaveAttribute("data-theme", "light");
		const stored = await page.evaluate(
			(key: string) => window.localStorage.getItem(key),
			THEME_KEY,
		);
		expect(stored).toBe("light");
		// Toggle back — dark again, still within same render, no reload.
		const candidateAgain = page
			.getByRole("button", { name: /切换到亮色|切换到暗色|theme/i })
			.first();
		await candidateAgain.click();
		await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
		const storedAfter = await page.evaluate(
			(key: string) => window.localStorage.getItem(key),
			THEME_KEY,
		);
		expect(storedAfter).toBe("dark");
	});
});
