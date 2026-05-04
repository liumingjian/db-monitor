"use client";

import { ChevronDown } from "lucide-react";
import { type SelectHTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
	readonly error?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>((props, ref) => {
	const { className, error = false, disabled, children, ...rest } = props;
	return (
		<div
			className={cn(
				"relative inline-flex h-9 w-full items-center rounded-md border bg-bg-elevated text-sm text-fg-primary focus-within:ring-2 focus-within:ring-ring",
				error ? "border-sev-critical" : "border-border-subtle",
				disabled && "opacity-60",
				className,
			)}
		>
			<select
				ref={ref}
				disabled={disabled}
				aria-invalid={error || undefined}
				className="h-full w-full appearance-none bg-transparent pl-3 pr-8 text-fg-primary outline-none disabled:cursor-not-allowed"
				{...rest}
			>
				{children}
			</select>
			<span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-fg-muted">
				<ChevronDown size={16} aria-hidden="true" />
			</span>
		</div>
	);
});
Select.displayName = "Select";
