import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";

const BASE = "http://127.0.0.1:3000";
const SHOTS = new URL("./screenshots/", import.meta.url).pathname;
mkdirSync(SHOTS, { recursive: true });

const results = [];
function record(name, ok, detail = "") {
	results.push({ name, ok, detail });
	const mark = ok ? "✓" : "✗";
	console.log(`${mark} ${name}${detail ? ` — ${detail}` : ""}`);
}

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();

page.on("console", (msg) => {
	if (msg.type() === "error") console.log(`  [console.error] ${msg.text()}`);
});
page.on("pageerror", (err) => console.log(`  [pageerror] ${err.message}`));

async function shot(name) {
	await page.screenshot({ path: `${SHOTS}${name}.png`, fullPage: true });
}

// 1. Login page loads
try {
	const res = await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
	await shot("01-login");
	record("login page responds 200", res?.status() === 200, `status=${res?.status()}`);
} catch (err) {
	record("login page loads", false, err.message);
}

// 2. Submit admin credentials
try {
	await page.fill('input[name="username"], input#username', "admin");
	await page.fill('input[name="password"], input#password', "admin-password");
	const [nav] = await Promise.all([
		page.waitForURL((url) => !url.pathname.startsWith("/login"), { timeout: 10_000 }),
		page.click('button[type="submit"]'),
	]);
	await shot("02-dashboard");
	record("admin login redirects away from /login", true, `url=${page.url()}`);
} catch (err) {
	record("admin login", false, err.message);
	await shot("02-login-failure");
}

// 3. Dashboard key sections rendered
try {
	const title = await page.title();
	const bodyText = (await page.locator("body").innerText()).slice(0, 400);
	record("dashboard title present", Boolean(title), title);
	record("dashboard non-empty body", bodyText.length > 50, `${bodyText.length} chars`);
} catch (err) {
	record("dashboard content", false, err.message);
}

// 4. Alerts page
try {
	await page.goto(`${BASE}/alerts`, { waitUntil: "networkidle" });
	await shot("03-alerts");
	const hasTable = await page.locator("table, [role='table']").count();
	record("alerts page renders", hasTable > 0 || (await page.locator("body").innerText()).length > 100);
} catch (err) {
	record("alerts page", false, err.message);
}

// 5. Rules
try {
	await page.goto(`${BASE}/rules`, { waitUntil: "networkidle" });
	await shot("04-rules");
	const url = page.url();
	record("rules page accessible", !url.includes("/login"), url);
} catch (err) {
	record("rules page", false, err.message);
}

// 6. NEW: notify-history page
try {
	const res = await page.goto(`${BASE}/admin/notify-history`, { waitUntil: "networkidle" });
	await shot("05-notify-history");
	const headerText = (await page.locator("h1, h2, h3").first().innerText().catch(() => "")) || "";
	const bodyText = await page.locator("body").innerText();
	record(
		"notify-history page loads (Epic 16 new)",
		res?.status() === 200 && !page.url().includes("/login"),
		`status=${res?.status()} header="${headerText}"`,
	);
	record("notify-history shows table or empty state", /history|notify|投递|empty|no|record/i.test(bodyText));
} catch (err) {
	record("notify-history page", false, err.message);
}

// 7. Instances
try {
	await page.goto(`${BASE}/instances`, { waitUntil: "networkidle" });
	await shot("06-instances");
	record("instances page accessible", !page.url().includes("/login"));
	const instanceLink = page.locator('a[href^="/instances/"]').first();
	if (await instanceLink.count()) {
		const href = await instanceLink.getAttribute("href");
		await page.goto(`${BASE}${href}`, { waitUntil: "networkidle" });
		await shot("07-instance-detail");
		record("instance detail page accessible", !page.url().includes("/login"), href);
	} else {
		record("instance detail page accessible", false, "no instance link found");
	}
} catch (err) {
	record("instances", false, err.message);
}

// 8. Overview
try {
	await page.goto(`${BASE}/overview`, { waitUntil: "networkidle" });
	await shot("08-overview");
	record("overview page accessible", !page.url().includes("/login"));
} catch (err) {
	record("overview", false, err.message);
}

// 9. Settings
try {
	await page.goto(`${BASE}/settings`, { waitUntil: "networkidle" });
	await shot("09-settings");
	record("settings page accessible", !page.url().includes("/login"));
} catch (err) {
	record("settings", false, err.message);
}

await browser.close();

const passed = results.filter((r) => r.ok).length;
console.log(`\n=== ${passed}/${results.length} checks passed ===`);
console.log(`screenshots: ${SHOTS}`);
process.exit(passed === results.length ? 0 : 1);
