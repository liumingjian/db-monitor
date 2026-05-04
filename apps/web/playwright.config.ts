import { defineConfig, devices } from "@playwright/test";

/**
 * Slice 1.5 child #10 — E2E + visual regression + Lighthouse gate.
 *
 * Run against the already-running `apps/web` (http://127.0.0.1:3000) and
 * `apps/api` (http://127.0.0.1:8000). The webServer block auto-starts
 * `pnpm --filter web dev` on demand; reuse the existing instance if already up
 * (CI or local Boss-driven dev loop).
 */
const baseURL = process.env.DB_MONITOR_E2E_BASE_URL ?? "http://127.0.0.1:3000";

export default defineConfig({
	expect: {
		timeout: 10_000,
		toHaveScreenshot: {
			animations: "disabled",
			caret: "hide",
			maxDiffPixelRatio: 0.03,
			scale: "css",
		},
	},
	fullyParallel: false,
	projects: [
		{
			name: "chromium",
			use: {
				...devices["Desktop Chrome"],
				viewport: { width: 1440, height: 900 },
			},
		},
	],
	reporter: [["list"]],
	retries: 1,
	testDir: "./tests-e2e",
	timeout: 60_000,
	use: {
		baseURL,
		ignoreHTTPSErrors: true,
		screenshot: "only-on-failure",
		trace: "retain-on-failure",
		video: "retain-on-failure",
	},
	webServer: {
		// Use production `next start` (no dev HMR) so React hydrates reliably.
		// Expects `pnpm --filter web build` to have been run beforehand; the
		// `test:e2e` script in package.json chains build + start where needed.
		command: "pnpm --filter web exec next start --port 3000",
		cwd: "../..",
		env: {
			DB_MONITOR_API_BASE_URL: process.env.DB_MONITOR_API_BASE_URL ?? "http://127.0.0.1:8000",
		},
		reuseExistingServer: true,
		timeout: 120_000,
		url: baseURL,
	},
	workers: 1,
});
