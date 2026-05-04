import type { AlertRuleResponse, InstanceResponse } from "@db-monitor/api-client";
import type { CommandItem } from "@db-monitor/ui";
import { getTranslations } from "next-intl/server";
import { NextResponse } from "next/server";

import { createServerApiClient, fetchServerSession } from "../../../src/server-api";

const NAV_ROUTES: readonly { readonly key: string; readonly href: string }[] = [
	{ key: "overview", href: "/overview" },
	{ key: "instances", href: "/instances" },
	{ key: "alerts", href: "/alerts" },
	{ key: "rules", href: "/rules" },
	{ key: "notifyHistory", href: "/admin/notify-history" },
	{ key: "channels", href: "/admin/channels" },
	{ key: "settings", href: "/settings" },
	{ key: "audit", href: "/admin/audit" },
];

export async function GET(): Promise<Response> {
	const session = await fetchServerSession();
	if (session === null) {
		return NextResponse.json({ error: "unauthenticated" }, { status: 401 });
	}

	const [navItems, instances, rules] = await Promise.all([
		buildNavItems(),
		safeListInstances(),
		safeListRules(),
	]);

	const items: readonly CommandItem[] = [...navItems, ...instances, ...rules];
	return NextResponse.json({ items });
}

async function buildNavItems(): Promise<readonly CommandItem[]> {
	const tNav = await getTranslations("nav");
	const tPalette = await getTranslations("commandPalette");
	return NAV_ROUTES.map((route) => {
		const label = tNav(route.key);
		const hint = tPalette("navHint");
		return {
			id: `nav:${route.href}`,
			kind: "nav" as const,
			label,
			hint,
			href: route.href,
			searchText: `${label} ${route.href}`,
		};
	});
}

async function safeListInstances(): Promise<readonly CommandItem[]> {
	try {
		const api = await createServerApiClient();
		const instances = await api.listInstances();
		return instances.map(instanceToCommandItem);
	} catch (error) {
		console.warn("[command-palette] listInstances failed:", error);
		return [];
	}
}

async function safeListRules(): Promise<readonly CommandItem[]> {
	try {
		const api = await createServerApiClient();
		const rules = await api.listRules();
		return rules.map(ruleToCommandItem);
	} catch (error) {
		console.warn("[command-palette] listRules failed:", error);
		return [];
	}
}

function instanceToCommandItem(instance: InstanceResponse): CommandItem {
	const hint = `${instance.engine.toUpperCase()} · ${instance.environment}`;
	return {
		id: `instance:${instance.instance_id}`,
		kind: "instance",
		label: instance.name,
		hint,
		href: `/instances/${instance.instance_id}`,
		searchText: `${instance.name} ${instance.environment} ${instance.engine} ${instance.instance_id}`,
	};
}

function ruleToCommandItem(rule: AlertRuleResponse): CommandItem {
	const hint = `${rule.metric_name} · ${rule.severity}`;
	return {
		id: `rule:${rule.rule_id}`,
		kind: "rule",
		label: rule.name,
		hint,
		href: `/rules/${rule.rule_id}`,
		searchText: `${rule.name} ${rule.metric_name} ${rule.severity} ${rule.engine}`,
	};
}
