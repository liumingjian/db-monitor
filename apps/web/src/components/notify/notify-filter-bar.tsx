"use client";

import { Button, Input, Label } from "@db-monitor/ui";
import { useTranslations } from "next-intl";

const CHANNEL_OPTIONS = ["feishu", "smtp"] as const;
const STATUS_OPTIONS = ["delivered", "failed", "skipped", "pending"] as const;
const LIMIT_OPTIONS = [50, 100, 200, 500] as const;
const DEFAULT_LIMIT = 100;

export interface NotifyFilterValues {
	readonly channel: string;
	readonly status: string;
	readonly ruleId: string;
	readonly instanceId: string;
	readonly limit: number;
}

export function parseNotifyFilters(
	searchParams: Record<string, string | string[] | undefined>,
): NotifyFilterValues {
	const pick = (key: string): string => {
		const value = searchParams[key];
		if (typeof value === "string") {
			return value;
		}
		if (Array.isArray(value) && typeof value[0] === "string") {
			return value[0];
		}
		return "";
	};
	const limitRaw = pick("limit");
	const limitNum = Number.parseInt(limitRaw, 10);
	const limit = Number.isFinite(limitNum) && limitNum > 0 ? Math.min(limitNum, 500) : DEFAULT_LIMIT;
	return {
		channel: pick("channel"),
		instanceId: pick("instance_id"),
		limit,
		ruleId: pick("rule_id"),
		status: pick("status"),
	};
}

export function notifyFiltersHasAny(filters: NotifyFilterValues): boolean {
	return (
		filters.channel.length > 0 ||
		filters.status.length > 0 ||
		filters.ruleId.length > 0 ||
		filters.instanceId.length > 0
	);
}

export interface NotifyFilterBarProps {
	readonly defaults: NotifyFilterValues;
}

/**
 * GET-method form that round-trips filters through the URL. Each change applies
 * via the native submit button; the "clear" anchor drops all filters.
 */
export function NotifyFilterBar({ defaults }: NotifyFilterBarProps) {
	const t = useTranslations("notifyHistory");
	return (
		<form
			action="/admin/notify-history"
			className="grid gap-3 rounded-md border border-border-hairline bg-bg-elevated p-4 md:grid-cols-5"
			method="get"
		>
			<div className="flex flex-col gap-1.5">
				<Label htmlFor="filter-channel">{t("filterChannel")}</Label>
				<select
					className="h-9 rounded-md border border-border-hairline bg-bg-base px-2 text-sm text-fg-primary"
					defaultValue={defaults.channel}
					id="filter-channel"
					name="channel"
				>
					<option value="">{t("filterAnyChannel")}</option>
					{CHANNEL_OPTIONS.map((option) => (
						<option key={option} value={option}>
							{option}
						</option>
					))}
				</select>
			</div>
			<div className="flex flex-col gap-1.5">
				<Label htmlFor="filter-status">{t("filterStatus")}</Label>
				<select
					className="h-9 rounded-md border border-border-hairline bg-bg-base px-2 text-sm text-fg-primary"
					defaultValue={defaults.status}
					id="filter-status"
					name="status"
				>
					<option value="">{t("filterAnyStatus")}</option>
					{STATUS_OPTIONS.map((option) => (
						<option key={option} value={option}>
							{option}
						</option>
					))}
				</select>
			</div>
			<div className="flex flex-col gap-1.5">
				<Label htmlFor="filter-rule">{t("filterRule")}</Label>
				<Input
					defaultValue={defaults.ruleId}
					id="filter-rule"
					name="rule_id"
					placeholder={t("filterPlaceholderRule")}
				/>
			</div>
			<div className="flex flex-col gap-1.5">
				<Label htmlFor="filter-instance" title={t("filterInstanceHint")}>
					{t("filterInstance")}
				</Label>
				<Input
					defaultValue={defaults.instanceId}
					id="filter-instance"
					name="instance_id"
					placeholder={t("filterPlaceholderInstance")}
				/>
				<span className="text-[11px] text-fg-muted">{t("filterInstanceHint")}</span>
			</div>
			<div className="flex flex-col gap-1.5">
				<Label htmlFor="filter-limit">{t("limitLabel")}</Label>
				<select
					className="h-9 rounded-md border border-border-hairline bg-bg-base px-2 text-sm font-mono tabular-nums text-fg-primary"
					defaultValue={String(defaults.limit)}
					id="filter-limit"
					name="limit"
				>
					{LIMIT_OPTIONS.map((option) => (
						<option key={option} value={option}>
							{option}
						</option>
					))}
				</select>
			</div>
			<div className="flex items-end gap-2 md:col-span-5">
				<Button size="sm" type="submit">
					{t("filterApply")}
				</Button>
				<a className="text-sm font-medium text-accent hover:underline" href="/admin/notify-history">
					{t("filterClear")}
				</a>
			</div>
		</form>
	);
}

export const NOTIFY_DEFAULT_LIMIT = DEFAULT_LIMIT;
