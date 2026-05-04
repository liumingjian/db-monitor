import { type VariantProps, cva } from "class-variance-authority";
import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

const badgeVariants = cva(
	"inline-flex items-center gap-1 rounded-md border font-medium whitespace-nowrap",
	{
		variants: {
			variant: {
				default: "border-transparent bg-accent text-on-accent",
				outline: "border-border-subtle bg-transparent text-fg-primary",
				secondary: "border-transparent bg-surface-overlay text-fg-secondary",
				destructive: "border-sev-critical-border bg-sev-critical-bg text-sev-critical",
				warning: "border-sev-warning-border bg-sev-warning-bg text-sev-warning",
				info: "border-sev-info-border bg-sev-info-bg text-sev-info",
				ok: "border-sev-ok-border bg-sev-ok-bg text-sev-ok",
			},
			size: {
				sm: "px-1.5 py-0 text-[11px] leading-4",
				md: "px-2 py-0.5 text-xs",
			},
		},
		defaultVariants: {
			variant: "default",
			size: "md",
		},
	},
);

export interface BadgeProps
	extends HTMLAttributes<HTMLSpanElement>,
		VariantProps<typeof badgeVariants> {}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>((props, ref) => {
	const { className, variant, size, ...rest } = props;
	return <span ref={ref} className={cn(badgeVariants({ variant, size }), className)} {...rest} />;
});
Badge.displayName = "Badge";

export { badgeVariants };
