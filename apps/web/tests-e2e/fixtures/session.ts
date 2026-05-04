import type { Page } from "@playwright/test";

/**
 * Credentials resolved from env vars — never hard-coded.
 * Defaults match the backend seed admin (admin/admin-password) documented in
 * smoke/phase-one.spec.ts so local runs work out of the box.
 */
export const E2E_USERNAME = process.env.DB_MONITOR_E2E_USERNAME ?? "admin";
export const E2E_PASSWORD = process.env.DB_MONITOR_E2E_PASSWORD ?? "admin-password";

/**
 * Drive the real /api/login endpoint (no mocks).
 *
 * 1. Navigate to /login
 * 2. Fill real credentials
 * 3. Submit and wait for the post-login redirect (default /overview)
 */
export async function loginAsAdmin(page: Page, nextPath = "/overview"): Promise<void> {
	await page.goto(`/login?next=${encodeURIComponent(nextPath)}`);
	// Ensure hydration completes so the form onSubmit handler takes precedence
	// over the native action={/api/login} fallback.
	await page.waitForLoadState("networkidle");
	await page.waitForTimeout(400);
	await page.getByLabel("用户名").fill(E2E_USERNAME);
	await page.getByLabel("密码").fill(E2E_PASSWORD);
	const [expectedPath, expectedQuery] = nextPath.split("?", 2);
	await Promise.all([
		page.waitForURL(
			(url) => {
				if (url.pathname !== expectedPath) return false;
				if (!expectedQuery) return true;
				const want = new URLSearchParams(expectedQuery);
				for (const [k, v] of want) {
					if (url.searchParams.get(k) !== v) return false;
				}
				return true;
			},
			{ timeout: 20_000 },
		),
		page.getByRole("button", { name: "登录" }).click(),
	]);
}

/**
 * Force light theme by toggling before each test when needed. Reads
 * `<html data-theme>` after toggle so caller can assert persistence.
 */
export async function setTheme(page: Page, theme: "dark" | "light"): Promise<void> {
	await page.evaluate((next: string) => {
		document.documentElement.dataset.theme = next;
		try {
			window.localStorage.setItem("db-monitor:ui-theme", next);
		} catch {
			/* ignore */
		}
	}, theme);
}
