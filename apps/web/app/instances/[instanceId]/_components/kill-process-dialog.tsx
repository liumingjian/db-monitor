"use client";

import {
	Button,
	Dialog,
	DialogBody,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	Input,
	Label,
} from "@db-monitor/ui";
import { useActionState, useEffect, useState } from "react";

import { type KillProcessResult, killProcessAction } from "./kill-process-action";

interface KillProcessDialogProps {
	readonly instanceId: string;
	readonly processId: number;
	readonly user: string;
}

/**
 * Q13 规则 3：Kill 二次确认。
 *
 * 点 Kill → Dialog 弹窗 → 用户键入 thread_id 字符串精确匹配才启用确认按钮
 * （GitHub 删仓库 / Lepus 删库同款反误杀）；reason 必填；提交期间按钮 disabled
 * + pending 文案（无 spinner）。
 */
export function KillProcessDialog(props: KillProcessDialogProps) {
	const { instanceId, processId, user } = props;
	const [open, setOpen] = useState<boolean>(false);
	const [state, formAction, pending] = useActionState<KillProcessResult | null, FormData>(
		killProcessAction,
		null,
	);

	useEffect(() => {
		if (state?.ok && open) {
			setOpen(false);
		}
	}, [state, open]);

	return (
		<>
			<Button onClick={() => setOpen(true)} size="sm" type="button" variant="destructive">
				Kill
			</Button>
			<Dialog onOpenChange={setOpen} open={open}>
				<DialogContent className="w-[28rem]">
					<DialogHeader>
						<DialogTitle>确认 Kill 会话 #{processId}</DialogTitle>
						<DialogDescription>
							目标用户 <span className="font-mono tabular-nums">{user}</span>。为避免误杀，请在
							下方键入 thread_id <span className="font-mono tabular-nums">{processId}</span> 以
							解锁确认按钮。
						</DialogDescription>
					</DialogHeader>
					<KillDialogForm
						formAction={formAction}
						instanceId={instanceId}
						pending={pending}
						processId={processId}
						resultState={state}
					/>
				</DialogContent>
			</Dialog>
		</>
	);
}

interface KillDialogFormProps {
	readonly formAction: (formData: FormData) => void;
	readonly instanceId: string;
	readonly pending: boolean;
	readonly processId: number;
	readonly resultState: KillProcessResult | null;
}

function KillDialogForm(props: KillDialogFormProps) {
	const [confirmation, setConfirmation] = useState<string>("");
	const [reason, setReason] = useState<string>("");
	const confirmationMatch = confirmation.trim() === String(props.processId);
	const reasonValid = reason.trim().length > 0;
	const submittable = confirmationMatch && reasonValid && !props.pending;

	return (
		<form action={props.formAction}>
			<DialogBody className="flex flex-col gap-4">
				<input name="instance_id" type="hidden" value={props.instanceId} />
				<input name="process_id" type="hidden" value={props.processId} />
				<div className="flex flex-col gap-1.5">
					<Label htmlFor={`kill-confirm-${props.processId}`} required>
						输入 thread_id 确认
					</Label>
					<Input
						aria-describedby={`kill-confirm-hint-${props.processId}`}
						autoComplete="off"
						className="font-mono tabular-nums"
						id={`kill-confirm-${props.processId}`}
						name="confirm_thread_id"
						onChange={(event) => setConfirmation(event.currentTarget.value)}
						placeholder={String(props.processId)}
						value={confirmation}
					/>
					<p className="text-xs text-fg-muted" id={`kill-confirm-hint-${props.processId}`}>
						需精确匹配当前会话 <span className="font-mono tabular-nums">{props.processId}</span>{" "}
						才会 启用 Kill 按钮。
					</p>
				</div>
				<div className="flex flex-col gap-1.5">
					<Label htmlFor={`kill-reason-${props.processId}`} required>
						原因（记录审计）
					</Label>
					<textarea
						className="min-h-[4.5rem] rounded-md border border-border-subtle bg-bg-elevated px-3 py-2 text-sm text-fg-primary placeholder:text-fg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
						id={`kill-reason-${props.processId}`}
						name="reason"
						onChange={(event) => setReason(event.currentTarget.value)}
						placeholder="例如：runaway query 占用 connections"
						required
						value={reason}
					/>
				</div>
				<KillResultBanner state={props.resultState} />
			</DialogBody>
			<DialogFooter>
				<Button
					onClick={() => {
						setConfirmation("");
						setReason("");
					}}
					size="sm"
					type="reset"
					variant="ghost"
				>
					清空
				</Button>
				<Button disabled={!submittable} size="sm" type="submit" variant="destructive">
					{props.pending ? "处理中…" : "确认 Kill"}
				</Button>
			</DialogFooter>
		</form>
	);
}

interface KillResultBannerProps {
	readonly state: KillProcessResult | null;
}

function KillResultBanner({ state }: KillResultBannerProps) {
	if (state === null || state.ok) {
		return null;
	}
	return (
		<p
			className="rounded-md border border-sev-critical-border bg-sev-critical-bg px-3 py-2 text-xs font-semibold text-sev-critical"
			role="alert"
		>
			{state.message}
		</p>
	);
}
