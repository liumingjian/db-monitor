"use client";

import type { AlertRuleResponse } from "@db-monitor/api-client";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@db-monitor/ui";
import type { ReactNode } from "react";

export interface RuleDetailTabsCopy {
	readonly definition: string;
	readonly overrides: string;
	readonly notifications: string;
	readonly audit: string;
}

interface RuleDetailTabsProps {
	readonly rule: AlertRuleResponse;
	readonly copy: RuleDetailTabsCopy;
	readonly definition: ReactNode;
	readonly overrides: ReactNode;
	readonly notifications: ReactNode;
	readonly audit: ReactNode;
}

export function RuleDetailTabs({
	rule,
	copy,
	definition,
	overrides,
	notifications,
	audit,
}: RuleDetailTabsProps) {
	return (
		<Tabs defaultValue="definition" idBase={`rule-${rule.rule_id}`}>
			<TabsList>
				<TabsTrigger value="definition">{copy.definition}</TabsTrigger>
				<TabsTrigger value="overrides">{copy.overrides}</TabsTrigger>
				<TabsTrigger value="notifications">{copy.notifications}</TabsTrigger>
				<TabsTrigger value="audit">{copy.audit}</TabsTrigger>
			</TabsList>
			<TabsContent value="definition">{definition}</TabsContent>
			<TabsContent value="overrides">{overrides}</TabsContent>
			<TabsContent value="notifications">{notifications}</TabsContent>
			<TabsContent value="audit">{audit}</TabsContent>
		</Tabs>
	);
}
