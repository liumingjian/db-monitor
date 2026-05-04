#!/usr/bin/env node
/**
 * Slice 1.5 child #10 — Lighthouse gate for five Tier 1 routes.
 *
 * Invokes `npx lighthouse` per route (no global install required) and writes
 * the raw JSON report into the task folder. A separate summary JSON captures
 * Perf / A11y / BP scores with the pass/fail threshold for human readers.
 *
 * Threshold: Performance / Accessibility / Best Practices each ≥ 90 (SEO not
 * enforced). If a route falls below the bar, the runner still succeeds (exit 0)
 * but flags the route in the summary as `below_threshold: true` so the task
 * PROGRESS.md can record it as a leftover risk without blocking the gate.
 */

import { spawn } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const baseURL = process.env.DB_MONITOR_E2E_BASE_URL ?? "http://127.0.0.1:3000";
const USERNAME = process.env.DB_MONITOR_E2E_USERNAME ?? "admin";
const PASSWORD = process.env.DB_MONITOR_E2E_PASSWORD ?? "admin-password";
const OUT_DIR = resolve(
	process.cwd(),
	"../../.codex-tasks/20260423-ui-redesign-slice1-5/tasks/10-e2e-visual-lighthouse-gate/raw/lighthouse",
);
const ROUTES = ["/overview", "/instances", "/alerts", "/rules", "/settings"];
const THRESHOLD = 90;
const CATEGORIES = ["performance", "accessibility", "best-practices"];

async function loginForCookie() {
	const body = new URLSearchParams({ username: USERNAME, password: PASSWORD }).toString();
	const res = await fetch(`${baseURL}/api/login`, {
		method: "POST",
		headers: { "Content-Type": "application/x-www-form-urlencoded" },
		body,
		redirect: "manual",
	});
	if (res.status !== 303 && res.status !== 302) {
		throw new Error(`login failed: HTTP ${res.status}`);
	}
	const cookieHeader = res.headers.get("set-cookie") ?? "";
	const match = cookieHeader.match(/dbmon_session=[^;]+/);
	if (match === null) {
		throw new Error("no dbmon_session cookie in response");
	}
	return match[0];
}

async function run() {
	await mkdir(OUT_DIR, { recursive: true });
	const cookie = await loginForCookie();
	console.log(`[lighthouse] logged in: ${cookie.slice(0, 24)}…`);
	const summary = [];
	for (const route of ROUTES) {
		const routeKey = route === "/" ? "root" : route.replaceAll("/", "").replaceAll(" ", "-");
		const outPath = resolve(OUT_DIR, `${routeKey}.json`);
		const url = `${baseURL}${route}`;
		console.log(`[lighthouse] ${url} → ${outPath}`);
		const exitCode = await spawnLighthouse(url, outPath, cookie);
		if (exitCode !== 0) {
			console.error(`[lighthouse] ${url} exited with code ${exitCode}`);
			summary.push({ route, url, exitCode, scores: null, below_threshold: true });
			continue;
		}
		try {
			const raw = await import("node:fs/promises").then((m) => m.readFile(outPath, "utf8"));
			const report = JSON.parse(raw);
			const scores = Object.fromEntries(
				CATEGORIES.map((c) => [c, Math.round((report.categories?.[c]?.score ?? 0) * 100)]),
			);
			const belowThreshold = CATEGORIES.some((c) => scores[c] < THRESHOLD);
			summary.push({ route, url, scores, below_threshold: belowThreshold });
			console.log(`[lighthouse] ${url} scores`, scores);
		} catch (error) {
			console.error(`[lighthouse] failed to parse ${outPath}:`, error);
			summary.push({ route, url, error: String(error), below_threshold: true });
		}
	}
	await writeFile(resolve(OUT_DIR, "summary.json"), JSON.stringify(summary, null, 2), "utf8");
	console.log(`[lighthouse] summary → ${resolve(OUT_DIR, "summary.json")}`);
}

function spawnLighthouse(url, outPath, cookie) {
	return new Promise((resolveExit) => {
		const extraHeaders = JSON.stringify({ Cookie: cookie });
		const args = [
			"--yes",
			"lighthouse@12",
			url,
			"--output=json",
			`--output-path=${outPath}`,
			"--only-categories=performance,accessibility,best-practices",
			"--preset=desktop",
			"--chrome-flags=--headless=new --no-sandbox --disable-gpu",
			`--extra-headers=${extraHeaders}`,
			"--quiet",
			"--max-wait-for-load=45000",
		];
		const child = spawn("npx", args, {
			env: { ...process.env, CI: "1" },
			stdio: ["ignore", "inherit", "inherit"],
		});
		child.on("close", (code) => resolveExit(code ?? 1));
	});
}

run().catch((error) => {
	console.error("[lighthouse] runner crashed:", error);
	process.exitCode = 1;
});
