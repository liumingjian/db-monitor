"use client";

import { useActionState, useEffect, useRef, useState } from "react";

import { type KillProcessResult, killProcessAction } from "./kill-process-action";

interface KillProcessDialogProps {
	readonly instanceId: string;
	readonly processId: number;
	readonly user: string;
}

export function KillProcessDialog({ instanceId, processId, user }: KillProcessDialogProps) {
	const [open, setOpen] = useState<boolean>(false);
	const [state, formAction, pending] = useActionState<KillProcessResult | null, FormData>(
		killProcessAction,
		null,
	);
	const dialogRef = useRef<HTMLDialogElement | null>(null);
	useSyncDialogOpen(dialogRef, open, () => setOpen(false));
	useCloseOnSuccess(state, open, () => setOpen(false));

	return (
		<>
			<button
				className="rounded-[0.7rem] border border-[var(--accent)] bg-white px-3 py-1 text-xs font-semibold text-[var(--accent)] hover:bg-[var(--accent)] hover:text-white"
				onClick={() => setOpen(true)}
				type="button"
			>
				Kill
			</button>
			<dialog
				aria-labelledby={`kill-dialog-title-${processId}`}
				className="rounded-[1.2rem] border border-black/10 bg-white p-0 shadow-xl backdrop:bg-black/40"
				onClose={() => setOpen(false)}
				ref={dialogRef}
			>
				<form action={formAction} className="flex w-[22rem] flex-col gap-3 p-5" method="dialog">
					<h3
						className="text-lg font-semibold text-[var(--ink)]"
						id={`kill-dialog-title-${processId}`}
					>
						确认 Kill 会话 #{processId}
					</h3>
					<p className="text-sm text-[var(--muted)]">
						目标用户 <span className="font-mono">{user}</span>。请填写原因以记录审计。
					</p>
					<input name="instance_id" type="hidden" value={instanceId} />
					<input name="process_id" type="hidden" value={processId} />
					<label className="grid gap-1 text-sm" htmlFor={`kill-reason-${processId}`}>
						<span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
							Reason
						</span>
						<textarea
							className="min-h-[4rem] rounded-[0.7rem] border border-black/10 bg-white px-3 py-2 text-sm text-[var(--ink)]"
							id={`kill-reason-${processId}`}
							name="reason"
							placeholder="例如：runaway query 占用 connections"
							required
						/>
					</label>
					<KillResultBanner state={state} />
					<div className="flex justify-end gap-2">
						<button
							className="rounded-[0.7rem] border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-[var(--muted)] hover:text-[var(--ink)]"
							onClick={() => setOpen(false)}
							type="button"
						>
							取消
						</button>
						<button
							className="rounded-[0.7rem] bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
							disabled={pending}
							type="submit"
						>
							{pending ? "Killing…" : "Confirm kill"}
						</button>
					</div>
				</form>
			</dialog>
		</>
	);
}

interface KillResultBannerProps {
	readonly state: KillProcessResult | null;
}

function KillResultBanner({ state }: KillResultBannerProps) {
	if (state === null) {
		return null;
	}
	if (state.ok) {
		return (
			<output className="rounded-[0.7rem] border border-green-500/30 bg-green-50 px-3 py-2 text-xs font-semibold text-green-700">
				已发起 kill，{state.checkedAt}
			</output>
		);
	}
	return (
		<p
			className="rounded-[0.7rem] border border-red-500/30 bg-red-50 px-3 py-2 text-xs font-semibold text-red-700"
			role="alert"
		>
			{state.message}
		</p>
	);
}

function useSyncDialogOpen(
	dialogRef: { readonly current: HTMLDialogElement | null },
	open: boolean,
	onClose: () => void,
): void {
	useEffect(() => {
		const node = dialogRef.current;
		if (node === null) {
			return;
		}
		if (open && !node.open) {
			node.showModal();
			return;
		}
		if (!open && node.open) {
			node.close();
			onClose();
		}
	}, [dialogRef, open, onClose]);
}

function useCloseOnSuccess(
	state: KillProcessResult | null,
	open: boolean,
	onClose: () => void,
): void {
	useEffect(() => {
		if (state?.ok && open) {
			onClose();
		}
	}, [state, open, onClose]);
}
