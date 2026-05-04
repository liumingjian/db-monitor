import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>((props, ref) => {
	const { className, ...rest } = props;
	return (
		<div
			ref={ref}
			className={cn(
				"rounded-lg border border-border-hairline bg-bg-elevated text-fg-primary shadow-sm",
				className,
			)}
			{...rest}
		/>
	);
});
Card.displayName = "Card";

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return <div ref={ref} className={cn("flex flex-col gap-1.5 p-4", className)} {...rest} />;
	},
);
CardHeader.displayName = "CardHeader";

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<h3
				ref={ref}
				className={cn(
					"text-base font-semibold leading-6 tracking-tight text-fg-primary",
					className,
				)}
				{...rest}
			/>
		);
	},
);
CardTitle.displayName = "CardTitle";

export const CardDescription = forwardRef<
	HTMLParagraphElement,
	HTMLAttributes<HTMLParagraphElement>
>((props, ref) => {
	const { className, ...rest } = props;
	return <p ref={ref} className={cn("text-sm text-fg-muted", className)} {...rest} />;
});
CardDescription.displayName = "CardDescription";

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return <div ref={ref} className={cn("p-4 pt-0", className)} {...rest} />;
	},
);
CardContent.displayName = "CardContent";

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<div
				ref={ref}
				className={cn(
					"flex items-center gap-2 p-4 pt-0 border-t border-border-hairline",
					className,
				)}
				{...rest}
			/>
		);
	},
);
CardFooter.displayName = "CardFooter";
