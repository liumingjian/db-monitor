import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export interface SeparatorProps extends HTMLAttributes<HTMLDivElement> {
	readonly orientation?: "horizontal" | "vertical";
	readonly decorative?: boolean;
}

export const Separator = forwardRef<HTMLDivElement, SeparatorProps>((props, ref) => {
	const { className, orientation = "horizontal", decorative = true, ...rest } = props;
	const ariaProps = decorative
		? { role: "none" as const }
		: { role: "separator" as const, "aria-orientation": orientation };
	return (
		<div
			ref={ref}
			{...ariaProps}
			className={cn(
				"bg-border-hairline",
				orientation === "horizontal" ? "h-px w-full" : "h-full w-px",
				className,
			)}
			{...rest}
		/>
	);
});
Separator.displayName = "Separator";
