import { type VariantProps, cva } from "class-variance-authority";
import { type ButtonHTMLAttributes, forwardRef } from "react";
import { Slot } from "./slot";
import { cn } from "./utils";

const buttonVariants = cva(
	"inline-flex items-center justify-center gap-2 whitespace-nowrap font-medium transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 select-none",
	{
		variants: {
			variant: {
				default: "bg-accent text-on-accent hover:bg-accent-hover active:bg-accent-active",
				destructive: "bg-sev-critical text-on-accent hover:brightness-110 active:brightness-95",
				outline:
					"border border-border-subtle bg-transparent text-fg-primary hover:bg-surface-overlay",
				ghost: "bg-transparent text-fg-primary hover:bg-surface-overlay",
				link: "bg-transparent text-accent underline-offset-4 hover:underline p-0 h-auto",
			},
			size: {
				sm: "h-8 rounded-sm px-3 text-xs",
				md: "h-9 rounded-md px-4 text-sm",
				lg: "h-11 rounded-lg px-6 text-base",
				icon: "h-9 w-9 rounded-md p-0",
			},
		},
		defaultVariants: {
			variant: "default",
			size: "md",
		},
	},
);

export interface ButtonProps
	extends ButtonHTMLAttributes<HTMLButtonElement>,
		VariantProps<typeof buttonVariants> {
	readonly asChild?: boolean;
	readonly loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>((props, ref) => {
	const {
		asChild = false,
		loading = false,
		className,
		variant,
		size,
		disabled,
		children,
		...rest
	} = props;
	const Comp = asChild ? Slot : "button";
	const composedClassName = cn(
		buttonVariants({ variant, size }),
		loading && "pointer-events-none",
		className,
	);
	return (
		<Comp
			ref={ref as React.Ref<HTMLButtonElement>}
			className={composedClassName}
			disabled={disabled || loading}
			aria-busy={loading || undefined}
			{...rest}
		>
			{loading ? <span className="inline-flex animate-pulse">…</span> : children}
		</Comp>
	);
});
Button.displayName = "Button";

export { buttonVariants };
