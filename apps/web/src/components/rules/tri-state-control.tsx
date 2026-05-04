"use client";

import { Button, cn } from "@db-monitor/ui";

import type { EnabledTriState } from "../../rule-overrides-ui";

interface TriStateOption {
	readonly value: EnabledTriState;
	readonly label: string;
	readonly tone: "neutral" | "accent" | "danger";
}

interface TriStateControlProps {
	readonly value: EnabledTriState;
	readonly onChange: (next: EnabledTriState) => void;
	readonly options: readonly TriStateOption[];
	readonly ariaLabel: string;
	readonly disabled?: boolean;
}

export function TriStateControl({
	value,
	onChange,
	options,
	ariaLabel,
	disabled = false,
}: TriStateControlProps) {
	return (
		<fieldset
			aria-label={ariaLabel}
			className="inline-flex min-w-0 overflow-hidden rounded-md border border-border-subtle p-0"
		>
			{options.map((option) => {
				const active = option.value === value;
				return (
					<Button
						aria-pressed={active}
						className={cn(
							"h-8 rounded-none border-0 border-r border-border-subtle px-3 text-xs last:border-r-0",
							active
								? toneActiveClass(option.tone)
								: "bg-transparent text-fg-muted hover:bg-surface-overlay",
						)}
						disabled={disabled}
						key={option.value}
						onClick={() => onChange(option.value)}
						size="sm"
						type="button"
						variant="ghost"
					>
						{option.label}
					</Button>
				);
			})}
		</fieldset>
	);
}

function toneActiveClass(tone: TriStateOption["tone"]): string {
	if (tone === "accent") {
		return "bg-accent/15 text-accent";
	}
	if (tone === "danger") {
		return "bg-sev-critical/15 text-sev-critical";
	}
	return "bg-surface-overlay text-fg-primary";
}
