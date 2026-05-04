import { expect, test } from "@playwright/test";

import { loginAsAdmin, setTheme } from "../fixtures/session";

const THEMES = ["dark", "light"] as const;

const TIER1_ROUTES: ReadonlyArray<{ readonly key: string; readonly path: string }> = [
	{ key: "01-login", path: "/login" },
	{ key: "02-overview", path: "/overview" },
	{ key: "03-instances", path: "/instances" },
	{ key: "04-alerts", path: "/alerts" },
	{ key: "05-rules", path: "/rules" },
	{ key: "06-settings", path: "/settings" },
	{ key: "07-notify-history", path: "/admin/notify-history" },
	{ key: "08-channels", path: "/admin/channels" },
	{ key: "09-audit", path: "/admin/audit" },
	{ key: "10-alerts-timeline", path: "/alerts?tab=timeline" },
	{ key: "11-alerts-acknowledged", path: "/alerts?tab=acknowledged" },
	{ key: "12-overview-24h", path: "/overview?window=24h" },
];

/**
 * 24 baseline screenshots = 12 routes × 2 themes. First run must be
 * invoked with `--update-snapshots` to create the baseline, subsequent runs
 * compare pixel-by-pixel within `maxDiffPixelRatio` tolerance.
 */
for (const theme of THEMES) {
	test.describe(`visual regression — ${theme}`, () => {
		test.beforeEach(async ({ page }) => {
			// Login is only required for protected routes, but calling loginAsAdmin
			// for /login causes unnecessary nav — treat login separately below.
		});

		for (const route of TIER1_ROUTES) {
			test(`${theme} ${route.key} ${route.path}`, async ({ page }) => {
				if (route.path === "/login") {
					await page.goto(route.path);
				} else {
					// Login via default /overview, then navigate to the target path
					// (covers routes with query strings like /alerts?tab=timeline).
					await loginAsAdmin(page);
					if (route.path !== "/overview") {
						await page.goto(route.path);
					}
				}
				await setTheme(page, theme);
				await page.waitForLoadState("networkidle").catch(() => undefined);
				// Allow an extra frame for theme + skeleton to settle.
				await page.waitForTimeout(300);
				await expect(page).toHaveScreenshot(`${theme}-${route.key}.png`, {
					fullPage: true,
				});
			});
		}
	});
}
