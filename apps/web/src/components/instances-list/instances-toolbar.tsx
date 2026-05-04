"use client";

import { cn } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

import { type InstancesViewKey, SPARK_METRIC_KEYS, type SparkMetricKey, VIEW_KEYS } from "./types";

interface InstancesToolbarProps {
	readonly view: InstancesViewKey;
	readonly sparkMetric: SparkMetricKey;
	readonly onOpenCreate: () => void;
}

/**
 * 二级工具栏：view toggle（table/grid）+ sparkline metric toggle + 新建 CTA。
 *
 * view / spark 参数走 URL，保持刷新一致性；新建抽屉由父组件驱动。
 */
export function InstancesToolbar(props: InstancesToolbarProps) {
	const { view, sparkMetric, onOpenCreate } = props;
	const t = useTranslations("instancesPage");
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();

	const setParam = useCallback(
		(key: string, value: string) => {
			const next = new URLSearchParams(searchParams?.toString() ?? "");
			next.set(key, value);
			router.push(`${pathname}?${next.toString()}`);
		},
		[pathname, router, searchParams],
	);

	return (
		<div className="flex flex-wrap items-center justify-between gap-3 border-b border-border-hairline pb-3">
			<div className="flex flex-wrap items-center gap-4">
				<SegmentedGroup
					ariaLabel={t("viewToggleLabel")}
					activeValue={view}
					options={VIEW_KEYS.map((key) => ({
						value: key,
						label: t(`view_${key}`),
					}))}
					onChange={(value) => setParam("view", value)}
				/>
				<SegmentedGroup
					ariaLabel={t("sparkMetricLabel")}
					activeValue={sparkMetric}
					options={SPARK_METRIC_KEYS.map((key) => ({
						value: key,
						label: t(`sparkMetric_${key}`),
					}))}
					onChange={(value) => setParam("spark", value)}
				/>
			</div>
			<button
				className="inline-flex h-9 items-center gap-2 rounded-md bg-accent px-4 text-sm font-semibold text-on-accent transition-colors hover:bg-accent-hover"
				onClick={onOpenCreate}
				type="button"
			>
				{t("createCta")}
			</button>
		</div>
	);
}

interface SegmentedGroupProps<T extends string> {
	readonly ariaLabel: string;
	readonly activeValue: T;
	readonly options: ReadonlyArray<{ value: T; label: string }>;
	readonly onChange: (value: T) => void;
}

function SegmentedGroup<T extends string>(props: SegmentedGroupProps<T>) {
	const { ariaLabel, activeValue, options, onChange } = props;
	return (
		<fieldset
			aria-label={ariaLabel}
			className="inline-flex items-center gap-1 rounded-md border border-border-hairline bg-bg-base p-1"
		>
			{options.map((option) => {
				const isActive = option.value === activeValue;
				return (
					<button
						aria-pressed={isActive}
						className={cn(
							"rounded-sm px-3 py-1 text-xs font-medium transition-colors",
							isActive ? "bg-accent/15 text-accent" : "text-fg-muted hover:text-fg-primary",
						)}
						key={option.value}
						onClick={() => onChange(option.value)}
						type="button"
					>
						{option.label}
					</button>
				);
			})}
		</fieldset>
	);
}
