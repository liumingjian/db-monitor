import { type LabelHTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
	readonly required?: boolean;
}

export const Label = forwardRef<HTMLLabelElement, LabelProps>((props, ref) => {
	const { className, required = false, children, ...rest } = props;
	return (
		// biome-ignore lint/a11y/noLabelWithoutControl: primitive <Label> expects callers to pass htmlFor (or nest the control); enforcement happens at call site.
		<label
			ref={ref}
			className={cn(
				"inline-flex items-center gap-1 text-sm font-medium text-fg-secondary select-none",
				className,
			)}
			{...rest}
		>
			{children}
			{required ? (
				<span aria-hidden="true" className="text-sev-critical">
					*
				</span>
			) : null}
		</label>
	);
});
Label.displayName = "Label";
