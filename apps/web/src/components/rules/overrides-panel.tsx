"use client";

import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	cn,
} from "@db-monitor/ui";
import { useActionState, useId, useMemo, useState } from "react";

import type {
	UpdateRuleResult,
	updateRuleAction,
} from "../../../app/rules/[ruleId]/_components/update-rule-action";
import {
	type EnabledTriState,
	type OverrideDraftRow,
	buildEmptyDraftRow,
} from "../../rule-overrides-ui";

import {
	EditOverrideDialog,
	type EditOverrideDialogCopy,
	type InstanceOption,
} from "./edit-override-dialog";
import { TriStateControl } from "./tri-state-control";

export interface OverridesPanelCopy {
	readonly heading: string;
	readonly tips: string;
	readonly addOverride: string;
	readonly editOverride: string;
	readonly empty: string;
	readonly columnInstance: string;
	readonly columnThreshold: string;
	readonly columnEnabled: string;
	readonly columnActions: string;
	readonly delete: string;
	readonly save: string;
	readonly saving: string;
	readonly inheritedThreshold: string;
	readonly stateInherit: string;
	readonly stateOn: string;
	readonly stateOff: string;
	readonly errorSave: (message: string) => string;
	readonly savedBanner: string;
	readonly dialog: EditOverrideDialogCopy;
}

interface OverridesPanelProps {
	readonly ruleId: string;
	readonly ruleDefaultThreshold: number;
	readonly initialRows: readonly OverrideDraftRow[];
	readonly instances: readonly InstanceOption[];
	readonly copy: OverridesPanelCopy;
	readonly action: typeof updateRuleAction;
}

export function OverridesPanel({
	ruleId,
	ruleDefaultThreshold,
	initialRows,
	instances,
	copy,
	action,
}: OverridesPanelProps) {
	const [rows, setRows] = useState<readonly OverrideDraftRow[]>(initialRows);
	const [dialogDraft, setDialogDraft] = useState<OverrideDraftRow | null>(null);
	const [state, formAction, pending] = useActionState<UpdateRuleResult | null, FormData>(
		action,
		null,
	);
	const nextClientId = useNextClientId();

	const instanceLookup = useMemo(() => buildInstanceLookup(instances), [instances]);
	const existingInstanceIds = rows.map((row) => row.instanceId);

	const openAddDialog = () => {
		setDialogDraft(buildEmptyDraftRow(nextClientId()));
	};
	const openEditDialog = (row: OverrideDraftRow) => {
		setDialogDraft(row);
	};
	const closeDialog = () => {
		setDialogDraft(null);
	};
	const handleDialogSubmit = (submitted: OverrideDraftRow) => {
		setRows((prev) => upsertRow(prev, submitted));
		setDialogDraft(null);
	};
	const handleDeleteRow = (clientId: string) => {
		setRows((prev) => prev.filter((row) => row.clientId !== clientId));
	};
	const handleInlineEnabledChange = (clientId: string, enabled: EnabledTriState) => {
		setRows((prev) => prev.map((row) => (row.clientId === clientId ? { ...row, enabled } : row)));
	};

	return (
		<Card>
			<CardHeader>
				<CardTitle>{copy.heading}</CardTitle>
				<CardDescription>{copy.tips}</CardDescription>
			</CardHeader>
			<CardContent>
				<form action={formAction} className="space-y-4">
					<input name="rule_id" type="hidden" value={ruleId} />
					<HiddenRows rows={rows} />
					<div className="flex items-center justify-end">
						<Button onClick={openAddDialog} size="sm" type="button" variant="outline">
							{copy.addOverride}
						</Button>
					</div>
					<OverridesTable
						copy={copy}
						instanceLookup={instanceLookup}
						onDelete={handleDeleteRow}
						onEdit={openEditDialog}
						onInlineEnabledChange={handleInlineEnabledChange}
						rows={rows}
					/>
					<ResultBanner copy={copy} state={state} />
					<div className="flex justify-end">
						<Button disabled={pending} type="submit" variant="default">
							{pending ? copy.saving : copy.save}
						</Button>
					</div>
				</form>
			</CardContent>
			<EditOverrideDialog
				copy={copy.dialog}
				draft={dialogDraft}
				existingInstanceIds={existingInstanceIds}
				instances={instances}
				onClose={closeDialog}
				onSubmit={handleDialogSubmit}
				open={dialogDraft !== null}
				ruleDefaultThreshold={ruleDefaultThreshold}
			/>
		</Card>
	);
}

interface HiddenRowsProps {
	readonly rows: readonly OverrideDraftRow[];
}

function HiddenRows({ rows }: HiddenRowsProps) {
	return (
		<>
			{rows.map((row) => (
				<div key={row.clientId}>
					<input name="override_client_id" type="hidden" value={row.clientId} />
					<input
						name={`override_instance_id__${row.clientId}`}
						type="hidden"
						value={row.instanceId}
					/>
					<input name={`override_enabled__${row.clientId}`} type="hidden" value={row.enabled} />
					<input name={`override_threshold__${row.clientId}`} type="hidden" value={row.threshold} />
				</div>
			))}
		</>
	);
}

interface OverridesTableProps {
	readonly copy: OverridesPanelCopy;
	readonly instanceLookup: ReadonlyMap<string, InstanceOption>;
	readonly onDelete: (clientId: string) => void;
	readonly onEdit: (row: OverrideDraftRow) => void;
	readonly onInlineEnabledChange: (clientId: string, enabled: EnabledTriState) => void;
	readonly rows: readonly OverrideDraftRow[];
}

function OverridesTable({
	copy,
	instanceLookup,
	onDelete,
	onEdit,
	onInlineEnabledChange,
	rows,
}: OverridesTableProps) {
	if (rows.length === 0) {
		return (
			<div className="rounded-md border border-dashed border-border-hairline px-4 py-6 text-center text-sm text-fg-muted">
				{copy.empty}
			</div>
		);
	}
	return (
		<div className="overflow-hidden rounded-md border border-border-hairline">
			<table className="w-full border-collapse text-sm">
				<thead className="bg-bg-subtle text-left text-xs font-semibold uppercase tracking-wide text-fg-muted">
					<tr>
						<th className="px-3 py-2">{copy.columnInstance}</th>
						<th className="px-3 py-2 text-right">{copy.columnThreshold}</th>
						<th className="px-3 py-2">{copy.columnEnabled}</th>
						<th className="px-3 py-2 text-right">{copy.columnActions}</th>
					</tr>
				</thead>
				<tbody>
					{rows.map((row) => (
						<OverridesRow
							copy={copy}
							instance={instanceLookup.get(row.instanceId) ?? null}
							key={row.clientId}
							onDelete={() => onDelete(row.clientId)}
							onEdit={() => onEdit(row)}
							onInlineEnabledChange={(next) => onInlineEnabledChange(row.clientId, next)}
							row={row}
						/>
					))}
				</tbody>
			</table>
		</div>
	);
}

interface OverridesRowProps {
	readonly copy: OverridesPanelCopy;
	readonly instance: InstanceOption | null;
	readonly onDelete: () => void;
	readonly onEdit: () => void;
	readonly onInlineEnabledChange: (next: EnabledTriState) => void;
	readonly row: OverrideDraftRow;
}

function OverridesRow({
	copy,
	instance,
	onDelete,
	onEdit,
	onInlineEnabledChange,
	row,
}: OverridesRowProps) {
	return (
		<tr className="border-t border-border-hairline">
			<td className="px-3 py-2">
				<span className={cn("font-medium text-fg-primary")}>
					{instance === null ? row.instanceId : instance.label}
				</span>
			</td>
			<td className="px-3 py-2 text-right font-mono tabular-nums">
				{row.threshold.length === 0 ? copy.inheritedThreshold : row.threshold}
			</td>
			<td className="px-3 py-2">
				<TriStateControl
					ariaLabel={copy.columnEnabled}
					onChange={onInlineEnabledChange}
					options={[
						{ value: "inherit", label: copy.stateInherit, tone: "neutral" },
						{ value: "on", label: copy.stateOn, tone: "accent" },
						{ value: "off", label: copy.stateOff, tone: "danger" },
					]}
					value={row.enabled}
				/>
			</td>
			<td className="px-3 py-2 text-right">
				<div className="inline-flex gap-2">
					<Button onClick={onEdit} size="sm" type="button" variant="outline">
						{copy.editOverride}
					</Button>
					<Button onClick={onDelete} size="sm" type="button" variant="ghost">
						{copy.delete}
					</Button>
				</div>
			</td>
		</tr>
	);
}

interface ResultBannerProps {
	readonly copy: OverridesPanelCopy;
	readonly state: UpdateRuleResult | null;
}

function ResultBanner({ copy, state }: ResultBannerProps) {
	if (state === null) {
		return null;
	}
	if (state.ok) {
		return (
			<output className="block rounded-md border border-sev-ok/30 bg-sev-ok/10 px-3 py-2 text-xs font-medium text-sev-ok">
				{copy.savedBanner}
			</output>
		);
	}
	return (
		<p
			className="rounded-md border border-sev-critical/40 bg-sev-critical/10 px-3 py-2 text-xs font-medium text-sev-critical"
			role="alert"
		>
			{copy.errorSave(state.message)}
		</p>
	);
}

function buildInstanceLookup(
	instances: readonly InstanceOption[],
): ReadonlyMap<string, InstanceOption> {
	const map = new Map<string, InstanceOption>();
	for (const instance of instances) {
		map.set(instance.id, instance);
	}
	return map;
}

function upsertRow(
	rows: readonly OverrideDraftRow[],
	submitted: OverrideDraftRow,
): readonly OverrideDraftRow[] {
	const existingIndex = rows.findIndex((row) => row.clientId === submitted.clientId);
	if (existingIndex < 0) {
		return [...rows, submitted];
	}
	const next = [...rows];
	next[existingIndex] = submitted;
	return next;
}

function useNextClientId(): () => string {
	const prefix = useId();
	const state = useMemo(() => ({ count: 0 }), []);
	return () => {
		state.count += 1;
		return `new-${prefix}-${state.count}`;
	};
}
