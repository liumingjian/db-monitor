import { type InputHTMLAttributes, type ReactNode, forwardRef } from "react";
import { cn } from "./utils";

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "prefix"> {
	readonly error?: boolean;
	readonly prefix?: ReactNode;
	readonly suffix?: ReactNode;
}

const baseInput =
	"w-full bg-transparent text-fg-primary placeholder:text-fg-muted outline-none disabled:cursor-not-allowed disabled:opacity-50";

const wrapper =
	"flex h-9 items-center gap-2 rounded-md border bg-bg-elevated px-3 text-sm transition-colors focus-within:ring-2 focus-within:ring-ring";

export const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => {
	const { className, error = false, prefix, suffix, type = "text", disabled, ...rest } = props;
	return (
		<div
			className={cn(
				wrapper,
				error ? "border-sev-critical" : "border-border-subtle",
				disabled && "opacity-60",
				className,
			)}
		>
			{prefix ? <span className="flex shrink-0 items-center text-fg-muted">{prefix}</span> : null}
			<input
				ref={ref}
				type={type}
				disabled={disabled}
				aria-invalid={error || undefined}
				className={cn(baseInput, "py-1")}
				{...rest}
			/>
			{suffix ? <span className="flex shrink-0 items-center text-fg-muted">{suffix}</span> : null}
		</div>
	);
});
Input.displayName = "Input";
