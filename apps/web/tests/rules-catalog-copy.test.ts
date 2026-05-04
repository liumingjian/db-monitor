import { describe, expect, it } from "vitest";

import { buildRulesCatalogCopy } from "../src/components/rules/rules-copy";

// Server-built copy is passed across the RSC boundary into a "use client"
// catalog component. Function-typed fields cannot be serialized into the RSC
// payload and surface as a 500 on cookie-only GET in production builds. This
// test guards against any future field re-introducing a function value.
describe("buildRulesCatalogCopy", () => {
	it("returns only string-valued fields (RSC-serializable)", () => {
		const fakeT = ((key: string) => key) as Parameters<typeof buildRulesCatalogCopy>[0];
		const copy = buildRulesCatalogCopy(fakeT, fakeT);
		for (const [key, value] of Object.entries(copy)) {
			expect(typeof value, `field ${key}`).toBe("string");
		}
	});
});
