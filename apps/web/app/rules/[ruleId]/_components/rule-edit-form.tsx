"use client";

import { useActionState, useId, useMemo, useState } from "react";

import {
	ENABLED_TRI_STATES,
	ENABLED_TRI_STATE_LABELS,
	type EnabledTriState,
	type OverrideDraftRow,
	buildEmptyDraftRow,
} from "../../../../src/rule-overrides-ui";

import { type UpdateRuleResult, updateRuleAction } from "./update-rule-action";

export interface InstanceOption {
	readonly id: string;
	readonly label: string;
}

interface RuleEditFormProps {
	readonly initialRows: readonly OverrideDraftRow[];
	readonly instances: readonly InstanceOption[];
	readonly ruleId: string;
}

export function RuleEditForm({ initialRows, instances, ruleId }: RuleEditFormProps) {
	const [rows, setRows] = useState<readonly OverrideDraftRow[]>(initialRows);
	const [state, formAction, pending] = useActionState<UpdateRuleResult | null, FormData>(
		updateRuleAction,
		null,
	);
	const nextClientIdRef = useNextClientId();

	return (
		<form action={formAction} className="space-y-4">
			<input name="rule_id" type="hidden" value={ruleId} />
			<div className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4">
				<div className="flex flex-wrap items-center justify-between gap-3">
					<h3 className="text-lg font-semibold">按实例覆盖</h3>
					<button
						className="rounded-[0.8rem] border border-[var(--accent)] bg-white px-3 py-1 text-xs font-semibold text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white"
						onClick={() => setRows((prev) => [...prev, buildEmptyDraftRow(nextClientIdRef())])}
						type="button"
					>
						+ 添加覆盖
					</button>
				</div>
				<OverrideTable
					instances={instances}
					onChange={(next) => setRows(next)}
					rows={rows}
				/>
			</div>
			<UpdateResultBanner state={state} />
			<button
				className="rounded-[0.8rem] bg-[var(--accent)] px-5 py-2 text-sm font-semibold text-white disabled:opacity-60"
				disabled={pending}
				type="submit"
			>
				{pending ? "保存中…" : "保存"}
			</button>
		</form>
	);
}

interface OverrideTableProps {
	readonly instances: readonly InstanceOption[];
	readonly onChange: (rows: readonly OverrideDraftRow[]) => void;
	readonly rows: readonly OverrideDraftRow[];
}

function OverrideTable({ instances, onChange, rows }: OverrideTableProps) {
	if (rows.length === 0) {
		return (
			<p className="mt-3 text-sm text-[var(--muted)]">
				尚无实例覆盖，点击“+ 添加覆盖”开始配置。
			</p>
		);
	}
	return (
		<table className="mt-3 w-full border-collapse text-sm" role="table">
			<thead>
				<tr className="text-left text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
					<th className="py-2 pr-3">实例</th>
					<th className="py-2 pr-3">阈值</th>
					<th className="py-2 pr-3">启停</th>
					<th className="py-2">操作</th>
				</tr>
			</thead>
			<tbody>
				{rows.map((row) => (
					<OverrideRow
						instances={instances}
						key={row.clientId}
						onChange={(updated) => onChange(replaceRow(rows, updated))}
						onDelete={() => onChange(removeRow(rows, row.clientId))}
						row={row}
					/>
				))}
			</tbody>
		</table>
	);
}

interface OverrideRowProps {
	readonly instances: readonly InstanceOption[];
	readonly onChange: (row: OverrideDraftRow) => void;
	readonly onDelete: () => void;
	readonly row: OverrideDraftRow;
}

function OverrideRow({ instances, onChange, onDelete, row }: OverrideRowProps) {
	return (
		<tr className="border-t border-black/5">
			<td className="py-2 pr-3">
				<InstanceSelect
					clientId={row.clientId}
					instances={instances}
					onChange={(value) => onChange({ ...row, instanceId: value })}
					value={row.instanceId}
				/>
			</td>
			<td className="py-2 pr-3">
				<ThresholdInput
					clientId={row.clientId}
					onChange={(value) => onChange({ ...row, threshold: value })}
					value={row.threshold}
				/>
			</td>
			<td className="py-2 pr-3">
				<EnabledSelect
					clientId={row.clientId}
					onChange={(value) => onChange({ ...row, enabled: value })}
					value={row.enabled}
				/>
			</td>
			<td className="py-2">
				<button
					aria-label="删除该覆盖"
					className="rounded-[0.6rem] border border-red-500/30 bg-white px-3 py-1 text-xs font-semibold text-red-600 hover:bg-red-50"
					onClick={onDelete}
					type="button"
				>
					删除
				</button>
			</td>
		</tr>
	);
}

interface InstanceSelectProps {
	readonly clientId: string;
	readonly instances: readonly InstanceOption[];
	readonly onChange: (value: string) => void;
	readonly value: string;
}

function InstanceSelect({ clientId, instances, onChange, value }: InstanceSelectProps) {
	return (
		<>
			<input name="override_client_id" type="hidden" value={clientId} />
			<select
				aria-label="实例"
				className="w-full rounded-[0.6rem] border border-black/10 bg-white px-2 py-1"
				name={`override_instance_id__${clientId}`}
				onChange={(event) => onChange(event.target.value)}
				required
				value={value}
			>
				<option value="">-- 选择实例 --</option>
				{instances.map((instance) => (
					<option key={instance.id} value={instance.id}>
						{instance.label}
					</option>
				))}
			</select>
		</>
	);
}

interface ThresholdInputProps {
	readonly clientId: string;
	readonly onChange: (value: string) => void;
	readonly value: string;
}

function ThresholdInput({ clientId, onChange, value }: ThresholdInputProps) {
	return (
		<input
			aria-label="阈值"
			className="w-28 rounded-[0.6rem] border border-black/10 bg-white px-2 py-1"
			inputMode="decimal"
			name={`override_threshold__${clientId}`}
			onChange={(event) => onChange(event.target.value)}
			placeholder="继承默认"
			type="text"
			value={value}
		/>
	);
}

interface EnabledSelectProps {
	readonly clientId: string;
	readonly onChange: (value: EnabledTriState) => void;
	readonly value: EnabledTriState;
}

function EnabledSelect({ clientId, onChange, value }: EnabledSelectProps) {
	return (
		<select
			aria-label="启停"
			className="rounded-[0.6rem] border border-black/10 bg-white px-2 py-1"
			name={`override_enabled__${clientId}`}
			onChange={(event) => onChange(event.target.value as EnabledTriState)}
			value={value}
		>
			{ENABLED_TRI_STATES.map((stateValue) => (
				<option key={stateValue} value={stateValue}>
					{ENABLED_TRI_STATE_LABELS[stateValue]}
				</option>
			))}
		</select>
	);
}

interface UpdateResultBannerProps {
	readonly state: UpdateRuleResult | null;
}

function UpdateResultBanner({ state }: UpdateResultBannerProps) {
	if (state === null || state.ok) {
		return null;
	}
	return (
		<p
			className="rounded-[0.8rem] border border-red-500/30 bg-red-50 px-3 py-2 text-xs font-semibold text-red-700"
			role="alert"
		>
			{state.message}
		</p>
	);
}

function useNextClientId(): () => string {
	const prefix = useId();
	const counterRef = useMemo(() => ({ count: 0 }), []);
	return () => {
		counterRef.count += 1;
		return `new-${prefix}-${counterRef.count}`;
	};
}

function replaceRow(
	rows: readonly OverrideDraftRow[],
	updated: OverrideDraftRow,
): readonly OverrideDraftRow[] {
	return rows.map((row) => (row.clientId === updated.clientId ? updated : row));
}

function removeRow(
	rows: readonly OverrideDraftRow[],
	clientId: string,
): readonly OverrideDraftRow[] {
	return rows.filter((row) => row.clientId !== clientId);
}
