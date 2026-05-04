"use client";

import { type ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export interface SwitchProps
	extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "onChange" | "type"> {
	readonly checked?: boolean;
	readonly indeterminate?: boolean;
	readonly onCheckedChange?: (next: boolean) => void;
}

export const Switch = forwardRef<HTMLButtonElement, SwitchProps>((props, ref) => {
	const {
		checked = false,
		indeterminate = false,
		onCheckedChange,
		disabled = false,
		className,
		onClick,
		onKeyDown,
		...rest
	} = props;

	const toggle = () => {
		if (disabled) {
			return;
		}
		onCheckedChange?.(!checked);
	};

	const ariaChecked: boolean | "mixed" = indeterminate ? "mixed" : checked;

	return (
		<button
			type="button"
			ref={ref}
			role="switch"
			aria-checked={ariaChecked}
			disabled={disabled}
			data-state={indeterminate ? "indeterminate" : checked ? "checked" : "unchecked"}
			onClick={(event) => {
				toggle();
				onClick?.(event);
			}}
			onKeyDown={(event) => {
				if (event.key === " " || event.key === "Enter") {
					event.preventDefault();
					toggle();
				}
				onKeyDown?.(event);
			}}
			className={cn(
				"relative inline-flex h-6 w-10 shrink-0 items-center rounded-full border border-border-subtle transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
				checked && !indeterminate ? "bg-accent" : "bg-surface-overlay",
				indeterminate && "bg-sev-warning-bg",
				className,
			)}
			{...rest}
		>
			<span
				aria-hidden="true"
				className={cn(
					"inline-block h-5 w-5 rounded-full bg-bg-elevated shadow-sm transition-transform",
					checked && !indeterminate ? "translate-x-4" : "translate-x-0.5",
					indeterminate && "translate-x-2",
				)}
			/>
		</button>
	);
});
Switch.displayName = "Switch";
