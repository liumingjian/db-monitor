"use client";

import { Button, Input, Select } from "@db-monitor/ui";
import { X as XIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { type FormEvent, useCallback, useMemo, useState } from "react";

const STATUS_CHOICES = ["passed", "failed"] as const;
type StatusChoice = (typeof STATUS_CHOICES)[number] | "";

interface InstancesFilterChipsProps {
	readonly initial: {
		readonly name: string;
		readonly environment: string;
		readonly label: string;
		readonly status: string;
	};
	readonly resultCount: number;
}

/**
 * 顶部 filter chip 条：env / status / label / name。
 *
 * 行为：
 * - 表单提交（Apply filters）→ router.push(pathname?...)，触发 server re-render
 * - 每个 active chip 右侧 × 单独移除（保留其它 chip + view + spark）
 * - 清除全部 → 清 env/status/label/name 四个参数，保留 view + spark
 */
export function InstancesFilterChips(props: InstancesFilterChipsProps) {
	const { initial, resultCount } = props;
	const t = useTranslations("instancesPage");
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();

	const [draftName, setDraftName] = useState(initial.name);
	const [draftEnvironment, setDraftEnvironment] = useState(initial.environment);
	const [draftLabel, setDraftLabel] = useState(initial.label);
	const [draftStatus, setDraftStatus] = useState<StatusChoice>(
		initial.status === "passed" || initial.status === "failed" ? initial.status : "",
	);

	const activeChips = useMemo(
		() =>
			[
				initial.name ? { key: "name", label: t("chipName", { value: initial.name }) } : null,
				initial.environment
					? { key: "environment", label: t("chipEnvironment", { value: initial.environment }) }
					: null,
				initial.label ? { key: "label", label: t("chipLabel", { value: initial.label }) } : null,
				initial.status
					? { key: "status", label: t("chipStatus", { value: initial.status }) }
					: null,
			].filter((entry): entry is { key: string; label: string } => entry !== null),
		[initial, t],
	);

	const pushWithParams = useCallback(
		(mutator: (params: URLSearchParams) => void) => {
			const next = new URLSearchParams(searchParams?.toString() ?? "");
			mutator(next);
			const query = next.toString();
			router.push(query.length === 0 ? pathname : `${pathname}?${query}`);
		},
		[pathname, router, searchParams],
	);

	const applyFilters = useCallback(
		(event: FormEvent<HTMLFormElement>) => {
			event.preventDefault();
			pushWithParams((params) => {
				setOrDelete(params, "name", draftName.trim());
				setOrDelete(params, "environment", draftEnvironment.trim());
				setOrDelete(params, "label", draftLabel.trim());
				setOrDelete(params, "status", draftStatus);
			});
		},
		[pushWithParams, draftName, draftEnvironment, draftLabel, draftStatus],
	);

	const removeChip = useCallback(
		(key: string) => {
			pushWithParams((params) => {
				params.delete(key);
			});
			if (key === "name") setDraftName("");
			if (key === "environment") setDraftEnvironment("");
			if (key === "label") setDraftLabel("");
			if (key === "status") setDraftStatus("");
		},
		[pushWithParams],
	);

	const clearAll = useCallback(() => {
		pushWithParams((params) => {
			for (const key of ["name", "environment", "label", "status"] as const) {
				params.delete(key);
			}
		});
		setDraftName("");
		setDraftEnvironment("");
		setDraftLabel("");
		setDraftStatus("");
	}, [pushWithParams]);

	return (
		<div className="flex flex-col gap-3 rounded-md border border-border-hairline bg-bg-base p-3">
			<form
				aria-label={t("filterFormLabel")}
				className="grid items-end gap-2 md:grid-cols-[1fr_1fr_1fr_1fr_auto]"
				onSubmit={applyFilters}
			>
				<div className="flex flex-col gap-1">
					<label
						htmlFor="instances-filter-name"
						className="text-[11px] font-medium uppercase tracking-wider text-fg-muted"
					>
						{t("filterName")}
					</label>
					<Input
						id="instances-filter-name"
						onChange={(event) => setDraftName(event.target.value)}
						placeholder={t("filterNamePlaceholder")}
						value={draftName}
					/>
				</div>
				<div className="flex flex-col gap-1">
					<label
						htmlFor="instances-filter-environment"
						className="text-[11px] font-medium uppercase tracking-wider text-fg-muted"
					>
						{t("filterEnvironment")}
					</label>
					<Input
						id="instances-filter-environment"
						onChange={(event) => setDraftEnvironment(event.target.value)}
						placeholder={t("filterEnvironmentPlaceholder")}
						value={draftEnvironment}
					/>
				</div>
				<div className="flex flex-col gap-1">
					<label
						htmlFor="instances-filter-label"
						className="text-[11px] font-medium uppercase tracking-wider text-fg-muted"
					>
						{t("filterLabel")}
					</label>
					<Input
						id="instances-filter-label"
						onChange={(event) => setDraftLabel(event.target.value)}
						placeholder={t("filterLabelPlaceholder")}
						value={draftLabel}
					/>
				</div>
				<div className="flex flex-col gap-1">
					<label
						htmlFor="instances-filter-status"
						className="text-[11px] font-medium uppercase tracking-wider text-fg-muted"
					>
						{t("filterStatus")}
					</label>
					<Select
						id="instances-filter-status"
						onChange={(event) => setDraftStatus(event.target.value as StatusChoice)}
						value={draftStatus}
					>
						<option value="">{t("filterStatusAll")}</option>
						{STATUS_CHOICES.map((choice) => (
							<option key={choice} value={choice}>
								{t(`filterStatus_${choice}`)}
							</option>
						))}
					</Select>
				</div>
				<Button size="sm" type="submit" variant="default">
					{t("filterApply")}
				</Button>
			</form>
			<div className="flex flex-wrap items-center gap-2 text-xs text-fg-muted">
				<span className="font-mono tabular-nums text-fg-secondary">
					{t("filterResultCount", { count: resultCount })}
				</span>
				{activeChips.length > 0 ? (
					<>
						<span aria-hidden="true" className="text-fg-disabled">
							·
						</span>
						{activeChips.map((chip) => (
							<button
								className="inline-flex items-center gap-1 rounded-sm border border-border-subtle bg-bg-elevated px-2 py-0.5 text-xs text-fg-primary hover:border-accent"
								key={chip.key}
								onClick={() => removeChip(chip.key)}
								type="button"
							>
								<span>{chip.label}</span>
								<XIcon aria-hidden="true" className="h-3 w-3" />
							</button>
						))}
						<button
							className="text-xs font-medium text-accent hover:underline"
							onClick={clearAll}
							type="button"
						>
							{t("filterClearAll")}
						</button>
					</>
				) : null}
			</div>
		</div>
	);
}

function setOrDelete(params: URLSearchParams, key: string, value: string): void {
	if (value.length === 0) {
		params.delete(key);
	} else {
		params.set(key, value);
	}
}
