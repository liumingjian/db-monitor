import { expect, test } from "@playwright/test";

const smokeInstanceDatabase = process.env.DB_MONITOR_SMOKE_INSTANCE_DATABASE ?? "mysql";
const smokeInstanceHost = process.env.DB_MONITOR_SMOKE_INSTANCE_HOST ?? "127.0.0.1";
const smokeInstancePassword = process.env.DB_MONITOR_SMOKE_INSTANCE_PASSWORD ?? "secret";
const smokeInstancePort = process.env.DB_MONITOR_SMOKE_INSTANCE_PORT ?? "3306";
const smokeInstanceUsername = process.env.DB_MONITOR_SMOKE_INSTANCE_USERNAME ?? "db_monitor";

test("phase-one release smoke flow", async ({ page }) => {
	await page.goto("/login");
	await page.getByLabel("Username").fill("admin");
	await page.getByLabel("Password").fill("admin-password");
	await page.getByRole("button", { name: "Sign in" }).click();
	await expect(page).toHaveURL(/\/overview$/);
	await expect(page.getByText("Fleet summary", { exact: true })).toBeVisible();
	await expect(page.locator("canvas").first()).toBeVisible();

	await page.goto("/instances/inst-prod-primary");
	await expect(page.getByRole("heading", { name: "prod-primary" })).toBeVisible();
	await expect(page.locator("canvas").first()).toBeVisible();

	await page.goto("/instances");
	await page.getByLabel("Name", { exact: true }).fill("smoke-secondary");
	await page.getByLabel("Environment").fill("stage");
	await page.getByLabel("Database").fill(smokeInstanceDatabase);
	await page.getByLabel("Host").fill(smokeInstanceHost);
	await page.getByLabel("Port").fill(smokeInstancePort);
	await page.getByLabel("Username").fill(smokeInstanceUsername);
	await page.getByLabel("Password").fill(smokeInstancePassword);
	await page.getByLabel("Labels").fill("smoke,secondary");
	await page.getByRole("button", { name: "Create and validate instance" }).click();
	await expect(page).toHaveURL(/\/instances\/inst-/);
	await expect(page.getByRole("heading", { name: "smoke-secondary" })).toBeVisible();

	await page.goto("/alerts");
	await expect(page.getByText("Replication Lag High")).toBeVisible();
	await page.getByText("Replication Lag High").first().click();
	await expect(page).toHaveURL(/\/alerts\/alert-lag$/);
	await expect(page.getByText("Notifier sent critical MySQL alert.")).toBeVisible();

	await page.goto("/rules");
	await page.getByLabel("Rule Name").fill("Connections High");
	await page.getByLabel("Metric Name").fill("mysql_threads_connected");
	await page.getByLabel("Threshold").fill("24");
	await page.getByLabel("Instance Scope").fill("inst-prod-primary");
	await page.getByLabel("Operator").selectOption("gte");
	await page.getByLabel("Severity").selectOption("warning");
	await page.getByRole("button", { name: "Create rule" }).click();
	await expect(page.getByText("Connections High")).toBeVisible();

	await page.goto("/settings");
	await page.getByLabel("notification.channel").fill("slack");
	await page.getByRole("button", { name: "Save setting" }).click();
	await expect(page.getByLabel("notification.channel")).toHaveValue("slack");
});
