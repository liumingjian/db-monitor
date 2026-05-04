"use client";

import type { AlertRuleResponse } from "@db-monitor/api-client";
import { Badge, Button, EntityBadge, Input, cn, formatTimestamp } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { useMemo, useState, useTransition } from "react";

import {
	type BatchRulesResult,
	setRulesEnabledAction,
} from "../../../app/rules/_actions/set-rules-enabled-action";
import {
	EMPTY_RULES_FILTERS,
	type EnabledFilterValue,
	type EngineFilterValue,
	type RulesCatalogFilters,
	type SeverityFilterValue,
	countOverrides,
	filterRules,
	formatScopeSummary,
} from "./rule-list-models";

interface RulesCatalogProps {
	readonly rules: readonly AlertRuleResponse[];
	readonly copy: RulesCatalogCopy;
}

export interface RulesCatalogCopy {
	readonly heading: string;
	readonly searchPlaceholder: string;
	readonly filterEngine: string;
	readonly filterSeverity: string;
	readonly filterEnabled: string;
	readonly filterAllEngines: string;
	readonly filterAllSeverities: string;
	readonly filterAllEnabled: string;
	readonly columnName: string;
	readonly columnEngine: string;
	readonly columnMetric: string;
	readonly columnThreshold: string;
	readonly columnSeverity: string;
	readonly columnEnabled: string;
	readonly columnOverrides: string;
	readonly columnActions: string;
	readonly empty: string;
	readonly enabledOn: string;
	readonly enabledOff: string;
	readonly batchEnable: string;
	readonly batchDisable: string;
	readonly batchClearSelection: string;
	readonly viewDetail: string;
}

export function RulesCatalog({ rules, copy }: RulesCatalogProps) {
	const t = useTranslations("rulesPage");
	const [filters, setFilters] = useState<RulesCatalogFilters>(EMPTY_RULES_FILTERS);
	const [selected, setSelected] = useState<ReadonlySet<string>>(() => new Set<string>());
	const [pending, startTransition] = useTransition();
	const [error, setError] = useState<string | null>(null);

	const visibleRules = useMemo(() => filterRules(rules, filters), [rules, filters]);
	const allVisibleSelected =
		visibleRules.length > 0 && visibleRules.every((rule) => selected.has(rule.rule_id));

	const handleToggleRule = (ruleId: string) => {
		setSelected((prev) => toggleValue(prev, ruleId));
	};
	const handleToggleAllVisible = () => {
		setSelected((prev) => toggleAllVisible(prev, visibleRules, allVisibleSelected));
	};
	const handleClearSelection = () => {
		setSelected(new Set<string>());
	};
	const runBatch = (enabled: boolean) => {
		if (selected.size === 0) {
			return;
		}
		setError(null);
		startTransition(async () => {
			const result = await setRulesEnabledAction({
				ruleIds: Array.from(selected),
				enabled,
			});
			handleBatchResult(result);
		});
	};
	const handleBatchResult = (result: BatchRulesResult) => {
		if (result.ok) {
			setSelected(new Set<string>());
			return;
		}
		setError(t("detail.errorSave", { message: result.message }));
	};

	return (
		<section aria-label={copy.heading} className="space-y-4">
			<CatalogFilters
				copy={copy}
				filters={filters}
				onChange={setFilters}
				totalLabel={t("catalog.countAll", { count: visibleRules.length })}
			/>
			<BatchBar
				copy={copy}
				disabled={pending}
				onClearSelection={handleClearSelection}
				onDisable={() => runBatch(false)}
				onEnable={() => runBatch(true)}
				rowsSelectedLabel={t("catalog.rowsSelected", { count: selected.size })}
				selectedCount={selected.size}
			/>
			{error !== null ? (
				<p className="rounded-md border border-sev-critical/40 bg-sev-critical/10 px-3 py-2 text-xs text-sev-critical">
					{error}
				</p>
			) : null}
			<CatalogTable
				allVisibleSelected={allVisibleSelected}
				copy={copy}
				onToggleAll={handleToggleAllVisible}
				onToggleRule={handleToggleRule}
				rules={visibleRules}
				selected={selected}
			/>
		</section>
	);
}

interface CatalogFiltersProps {
	readonly copy: RulesCatalogCopy;
	readonly filters: RulesCatalogFilters;
	readonly onChange: (next: RulesCatalogFilters) => void;
	readonly totalLabel: string;
}

function CatalogFilters({ copy, filters, onChange, totalLabel }: CatalogFiltersProps) {
	return (
		<div className="flex flex-wrap items-end gap-3">
			<div className="min-w-[220px] flex-1">
				<Input
					aria-label={copy.searchPlaceholder}
					onChange={(event) => onChange({ ...filters, query: event.target.value })}
					placeholder={copy.searchPlaceholder}
					value={filters.query}
				/>
			</div>
			<FilterSelect
				label={copy.filterEngine}
				onChange={(value) => onChange({ ...filters, engine: value as EngineFilterValue })}
				options={[
					{ value: "", label: copy.filterAllEngines },
					{ value: "mysql", label: "MySQL" },
					{ value: "oracle", label: "Oracle" },
				]}
				value={filters.engine}
			/>
			<FilterSelect
				label={copy.filterSeverity}
				onChange={(value) => onChange({ ...filters, severity: value as SeverityFilterValue })}
				options={[
					{ value: "", label: copy.filterAllSeverities },
					{ value: "warning", label: "warning" },
					{ value: "critical", label: "critical" },
				]}
				value={filters.severity}
			/>
			<FilterSelect
				label={copy.filterEnabled}
				onChange={(value) => onChange({ ...filters, enabled: value as EnabledFilterValue })}
				options={[
					{ value: "", label: copy.filterAllEnabled },
					{ value: "enabled", label: copy.enabledOn },
					{ value: "disabled", label: copy.enabledOff },
				]}
				value={filters.enabled}
			/>
			<span className="ml-auto text-xs text-fg-muted font-mono tabular-nums">{totalLabel}</span>
		</div>
	);
}

interface FilterSelectProps {
	readonly label: string;
	readonly value: string;
	readonly onChange: (value: string) => void;
	readonly options: readonly { readonly value: string; readonly label: string }[];
}

function FilterSelect({ label, value, onChange, options }: FilterSelectProps) {
	return (
		<label className="flex flex-col gap-1 text-xs font-medium text-fg-muted">
			<span>{label}</span>
			<select
				className="h-9 rounded-md border border-border-subtle bg-bg-elevated px-3 text-sm text-fg-primary outline-none focus-visible:ring-2 focus-visible:ring-ring"
				onChange={(event) => onChange(event.target.value)}
				value={value}
			>
				{options.map((option) => (
					<option key={option.value} value={option.value}>
						{option.label}
					</option>
				))}
			</select>
		</label>
	);
}

interface BatchBarProps {
	readonly copy: RulesCatalogCopy;
	readonly disabled: boolean;
	readonly onClearSelection: () => void;
	readonly onDisable: () => void;
	readonly onEnable: () => void;
	readonly rowsSelectedLabel: string;
	readonly selectedCount: number;
}

function BatchBar({
	copy,
	disabled,
	onClearSelection,
	onDisable,
	onEnable,
	rowsSelectedLabel,
	selectedCount,
}: BatchBarProps) {
	if (selectedCount === 0) {
		return null;
	}
	return (
		<div className="flex flex-wrap items-center gap-3 rounded-md border border-accent/40 bg-accent/10 px-3 py-2 text-xs text-fg-primary">
			<span className="font-semibold">{rowsSelectedLabel}</span>
			<div className="ml-auto flex flex-wrap items-center gap-2">
				<Button disabled={disabled} onClick={onEnable} size="sm" variant="outline">
					{copy.batchEnable}
				</Button>
				<Button disabled={disabled} onClick={onDisable} size="sm" variant="outline">
					{copy.batchDisable}
				</Button>
				<Button disabled={disabled} onClick={onClearSelection} size="sm" variant="ghost">
					{copy.batchClearSelection}
				</Button>
			</div>
		</div>
	);
}

interface CatalogTableProps {
	readonly allVisibleSelected: boolean;
	readonly copy: RulesCatalogCopy;
	readonly onToggleAll: () => void;
	readonly onToggleRule: (ruleId: string) => void;
	readonly rules: readonly AlertRuleResponse[];
	readonly selected: ReadonlySet<string>;
}

function CatalogTable({
	allVisibleSelected,
	copy,
	onToggleAll,
	onToggleRule,
	rules,
	selected,
}: CatalogTableProps) {
	if (rules.length === 0) {
		return (
			<div className="rounded-md border border-border-hairline bg-bg-elevated px-4 py-8 text-center text-sm text-fg-muted">
				{copy.empty}
			</div>
		);
	}
	return (
		<div className="overflow-hidden rounded-md border border-border-hairline">
			<table className="w-full border-collapse text-sm">
				<thead className="bg-bg-subtle text-left text-xs font-semibold uppercase tracking-wide text-fg-muted">
					<tr>
						<th className="w-10 px-3 py-2">
							<input
								aria-label="select all"
								checked={allVisibleSelected}
								className="h-4 w-4 accent-accent"
								onChange={onToggleAll}
								type="checkbox"
							/>
						</th>
						<th className="px-3 py-2">{copy.columnName}</th>
						<th className="px-3 py-2">{copy.columnEngine}</th>
						<th className="px-3 py-2">{copy.columnMetric}</th>
						<th className="px-3 py-2 text-right">{copy.columnThreshold}</th>
						<th className="px-3 py-2">{copy.columnSeverity}</th>
						<th className="px-3 py-2">{copy.columnEnabled}</th>
						<th className="px-3 py-2 text-right">{copy.columnOverrides}</th>
						<th className="px-3 py-2 text-right">{copy.columnActions}</th>
					</tr>
				</thead>
				<tbody>
					{rules.map((rule) => (
						<CatalogRow
							copy={copy}
							key={rule.rule_id}
							onToggle={() => onToggleRule(rule.rule_id)}
							rule={rule}
							selected={selected.has(rule.rule_id)}
						/>
					))}
				</tbody>
			</table>
		</div>
	);
}

interface CatalogRowProps {
	readonly copy: RulesCatalogCopy;
	readonly onToggle: () => void;
	readonly rule: AlertRuleResponse;
	readonly selected: boolean;
}

function CatalogRow({ copy, onToggle, rule, selected }: CatalogRowProps) {
	return (
		<tr
			className={cn(
				"border-t border-border-hairline hover:bg-surface-overlay",
				selected && "bg-accent/10",
			)}
		>
			<td className="px-3 py-2">
				<input
					aria-label={`select ${rule.name}`}
					checked={selected}
					className="h-4 w-4 accent-accent"
					onChange={onToggle}
					type="checkbox"
				/>
			</td>
			<td className="px-3 py-2">
				<div className="flex flex-col">
					<span className="font-medium text-fg-primary">{rule.name}</span>
					<span className="text-xs text-fg-muted">{formatScopeSummary(rule)}</span>
				</div>
			</td>
			<td className="px-3 py-2 text-xs uppercase tracking-wide text-fg-muted">{rule.engine}</td>
			<td className="px-3 py-2 font-mono text-xs text-fg-secondary tabular-nums">
				{rule.metric_name}
			</td>
			<td className="px-3 py-2 text-right font-mono tabular-nums">
				{rule.operator} {rule.threshold}
			</td>
			<td className="px-3 py-2">
				<EntityBadge
					label={rule.severity}
					tone={rule.severity === "critical" ? "critical" : "warning"}
				/>
			</td>
			<td className="px-3 py-2">
				<Badge variant={rule.enabled ? "default" : "outline"}>
					{rule.enabled ? copy.enabledOn : copy.enabledOff}
				</Badge>
			</td>
			<td className="px-3 py-2 text-right font-mono tabular-nums">{countOverrides(rule)}</td>
			<td className="px-3 py-2 text-right">
				<Button asChild size="sm" variant="outline">
					<Link href={`/rules/${rule.rule_id}`}>{copy.viewDetail}</Link>
				</Button>
			</td>
		</tr>
	);
}

function toggleValue<T>(set: ReadonlySet<T>, value: T): ReadonlySet<T> {
	const next = new Set(set);
	if (next.has(value)) {
		next.delete(value);
	} else {
		next.add(value);
	}
	return next;
}

function toggleAllVisible(
	previous: ReadonlySet<string>,
	visible: readonly AlertRuleResponse[],
	allSelected: boolean,
): ReadonlySet<string> {
	const next = new Set(previous);
	if (allSelected) {
		for (const rule of visible) {
			next.delete(rule.rule_id);
		}
	} else {
		for (const rule of visible) {
			next.add(rule.rule_id);
		}
	}
	return next;
}

// silence unused formatTimestamp warning (reserved for upcoming updated_at column)
void formatTimestamp;
