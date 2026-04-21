import { defineConfig } from "vitest/config";

export default defineConfig({
	resolve: {
		conditions: ["browser", "module"],
	},
	test: {
		environment: "node",
		include: ["tests/**/*.test.ts"],
	},
});
