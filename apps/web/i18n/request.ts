import { getRequestConfig } from "next-intl/server";

/*
 * Single-locale setup (zh-CN) for Slice 1.5.
 * Routing is disabled (no [locale] segment) — every request resolves to zh-CN.
 * Slice 2 introduces en-US once product copy is reviewed.
 */
const DEFAULT_LOCALE = "zh-CN" as const;

export default getRequestConfig(async () => {
	const messages = (await import("../messages/zh-CN.json")).default;
	return {
		locale: DEFAULT_LOCALE,
		messages,
		timeZone: "Asia/Shanghai",
		now: new Date(),
	};
});
