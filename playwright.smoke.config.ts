import { defineConfig } from "@playwright/test";

export default defineConfig({
	expect: {
		timeout: 10_000,
	},
	testDir: "./smoke",
	timeout: 60_000,
	use: {
		baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3010",
		browserName: "chromium",
		headless: true,
		trace: "retain-on-failure",
	},
	workers: 1,
});
