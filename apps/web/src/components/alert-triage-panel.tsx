import type { AlertDetailResponse } from "@db-monitor/api-client";

import {
	acknowledgeAlertAction,
	addAlertNoteAction,
	assignAlertOwnerAction,
} from "../monitoring-actions";

interface AlertTriagePanelProps {
	readonly alertDetail: AlertDetailResponse;
}

export function AlertTriagePanel({ alertDetail }: AlertTriagePanelProps) {
	const { record } = alertDetail;
	const engineLabel = record.engine === "oracle" ? "Oracle" : "MySQL";

	return (
		<div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_320px]">
			<div className="rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4">
				<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
					Workflow
				</p>
				<div className="mt-4 grid gap-3 md:grid-cols-4">
					<SummaryCard label="Engine" value={engineLabel} />
					<SummaryCard label="Status" value={record.status} />
					<SummaryCard label="Owner" value={record.owner_user_id ?? "unassigned"} />
					<SummaryCard label="Acknowledged" value={record.acknowledged_by_user_id ?? "pending"} />
				</div>
			</div>
			<div className="space-y-4 rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4">
				<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
					Actions
				</p>
				<AcknowledgeForm alertId={record.alert_id} />
				<AssignOwnerForm alertId={record.alert_id} ownerUserId={record.owner_user_id} />
				<AddNoteForm alertId={record.alert_id} />
			</div>
		</div>
	);
}

function SummaryCard({ label, value }: { readonly label: string; readonly value: string }) {
	return (
		<div className="rounded-[1rem] border border-black/5 bg-white/80 p-4">
			<p className="text-xs uppercase tracking-[0.24em] text-[var(--muted)]">{label}</p>
			<p className="mt-2 text-sm font-semibold text-[var(--ink)]">{value}</p>
		</div>
	);
}

function AcknowledgeForm({ alertId }: { readonly alertId: string }) {
	return (
		<form action={acknowledgeAlertAction} className="space-y-3">
			<input name="alert_id" type="hidden" value={alertId} />
			<button
				className="w-full rounded-[1rem] bg-[var(--accent)] px-4 py-3 text-sm font-semibold text-white"
				type="submit"
			>
				Acknowledge alert
			</button>
		</form>
	);
}

function AssignOwnerForm(props: { readonly alertId: string; readonly ownerUserId: string | null }) {
	return (
		<form action={assignAlertOwnerAction} className="space-y-3">
			<input name="alert_id" type="hidden" value={props.alertId} />
			<label className="block text-sm font-medium text-[var(--ink)]" htmlFor="owner_user_id">
				Assign owner
			</label>
			<input
				className="w-full rounded-[1rem] border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none transition focus:border-[var(--accent)]"
				defaultValue={props.ownerUserId ?? ""}
				id="owner_user_id"
				name="owner_user_id"
				placeholder="user-ops"
				type="text"
			/>
			<button
				className="w-full rounded-[1rem] border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-[var(--ink)]"
				type="submit"
			>
				Update owner
			</button>
		</form>
	);
}

function AddNoteForm({ alertId }: { readonly alertId: string }) {
	return (
		<form action={addAlertNoteAction} className="space-y-3">
			<input name="alert_id" type="hidden" value={alertId} />
			<label className="block text-sm font-medium text-[var(--ink)]" htmlFor="note">
				Add note
			</label>
			<textarea
				className="min-h-28 w-full rounded-[1rem] border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none transition focus:border-[var(--accent)]"
				id="note"
				name="note"
				placeholder="Investigating the engine signal, current threshold breach, and owner handoff context."
			/>
			<button
				className="w-full rounded-[1rem] border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-[var(--ink)]"
				type="submit"
			>
				Append note
			</button>
		</form>
	);
}
