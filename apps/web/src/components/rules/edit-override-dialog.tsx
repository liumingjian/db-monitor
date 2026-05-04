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
	cn,
} from "@db-monitor/ui";
import { useEffect, useState } from "react";

import type { EnabledTriState, OverrideDraftRow } from "../../rule-overrides-ui";

import { TriStateControl } from "./tri-state-control";

export interface InstanceOption {
	readonly id: string;
	readonly label: string;
}

export interface EditOverrideDialogCopy {
	readonly title: string;
	readonly description: string;
	readonly instanceLabel: string;
	readonly instancePlaceholder: string;
	readonly thresholdLabel: string;
	readonly thresholdPlaceholder: string;
	readonly enabledLabel: string;
	readonly stateInherit: string;
	readonly stateOn: string;
	readonly stateOff: string;
	readonly stateInheritHelp: string;
	readonly stateOnHelp: string;
	readonly stateOffHelp: string;
	readonly save: string;
	readonly cancel: string;
	readonly inheritedFromRule: (threshold: string) => string;
}

interface EditOverrideDialogProps {
	readonly open: boolean;
	readonly draft: OverrideDraftRow | null;
	readonly instances: readonly InstanceOption[];
	readonly existingInstanceIds: readonly string[];
	readonly ruleDefaultThreshold: number;
	readonly copy: EditOverrideDialogCopy;
	readonly onClose: () => void;
	readonly onSubmit: (row: OverrideDraftRow) => void;
}

export function EditOverrideDialog({
	open,
	draft,
	instances,
	existingInstanceIds,
	ruleDefaultThreshold,
	copy,
	onClose,
	onSubmit,
}: EditOverrideDialogProps) {
	const [local, setLocal] = useState<OverrideDraftRow | null>(draft);

	useEffect(() => {
		setLocal(draft);
	}, [draft]);

	if (local === null) {
		return null;
	}

	const availableInstances = filterAvailableInstances(
		instances,
		existingInstanceIds,
		local.instanceId,
	);
	const canSubmit = local.instanceId.length > 0;

	const handleChange = <K extends keyof OverrideDraftRow>(
		key: K,
		value: OverrideDraftRow[K],
	): void => {
		setLocal({ ...local, [key]: value });
	};

	const handleSubmit = () => {
		if (!canSubmit) {
			return;
		}
		onSubmit(local);
	};

	return (
		<Dialog onOpenChange={(next) => (next ? undefined : onClose())} open={open}>
			<DialogContent className="max-w-xl">
				<DialogHeader>
					<DialogTitle>{copy.title}</DialogTitle>
					<DialogDescription>{copy.description}</DialogDescription>
				</DialogHeader>
				<DialogBody className="space-y-4">
					<div className="flex flex-col gap-1.5">
						<Label htmlFor={`${local.clientId}-instance`} required>
							{copy.instanceLabel}
						</Label>
						<select
							className="h-9 rounded-md border border-border-subtle bg-bg-elevated px-3 text-sm text-fg-primary outline-none focus-visible:ring-2 focus-visible:ring-ring"
							id={`${local.clientId}-instance`}
							onChange={(event) => handleChange("instanceId", event.target.value)}
							value={local.instanceId}
						>
							<option value="">{copy.instancePlaceholder}</option>
							{availableInstances.map((instance) => (
								<option key={instance.id} value={instance.id}>
									{instance.label}
								</option>
							))}
						</select>
					</div>

					<div className="flex flex-col gap-1.5">
						<Label>{copy.enabledLabel}</Label>
						<TriStateControl
							ariaLabel={copy.enabledLabel}
							onChange={(next: EnabledTriState) => handleChange("enabled", next)}
							options={[
								{ value: "inherit", label: copy.stateInherit, tone: "neutral" },
								{ value: "on", label: copy.stateOn, tone: "accent" },
								{ value: "off", label: copy.stateOff, tone: "danger" },
							]}
							value={local.enabled}
						/>
						<p className="text-xs text-fg-muted">{describeStateHelp(local.enabled, copy)}</p>
					</div>

					<div className="flex flex-col gap-1.5">
						<Label htmlFor={`${local.clientId}-threshold`}>{copy.thresholdLabel}</Label>
						<Input
							className={cn("font-mono tabular-nums")}
							id={`${local.clientId}-threshold`}
							inputMode="decimal"
							onChange={(event) => handleChange("threshold", event.target.value)}
							placeholder={copy.thresholdPlaceholder}
							value={local.threshold}
						/>
						<p className="text-xs text-fg-muted">
							{copy.inheritedFromRule(String(ruleDefaultThreshold))}
						</p>
					</div>
				</DialogBody>
				<DialogFooter>
					<Button onClick={onClose} type="button" variant="ghost">
						{copy.cancel}
					</Button>
					<Button disabled={!canSubmit} onClick={handleSubmit} type="button" variant="default">
						{copy.save}
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
}

function describeStateHelp(state: EnabledTriState, copy: EditOverrideDialogCopy): string {
	if (state === "on") {
		return copy.stateOnHelp;
	}
	if (state === "off") {
		return copy.stateOffHelp;
	}
	return copy.stateInheritHelp;
}

function filterAvailableInstances(
	instances: readonly InstanceOption[],
	existingInstanceIds: readonly string[],
	currentInstanceId: string,
): readonly InstanceOption[] {
	const blocked = new Set(existingInstanceIds.filter((id) => id !== currentInstanceId));
	return instances.filter((instance) => !blocked.has(instance.id));
}
