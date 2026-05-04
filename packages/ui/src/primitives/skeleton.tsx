import { type HTMLAttributes, forwardRef } from "react";
import { cn } from "./utils";

export interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
	readonly width?: number | string;
	readonly height?: number | string;
	readonly rounded?: "sm" | "md" | "lg" | "full" | "none";
}

const roundedMap: Record<NonNullable<SkeletonProps["rounded"]>, string> = {
	sm: "rounded-sm",
	md: "rounded-md",
	lg: "rounded-lg",
	full: "rounded-full",
	none: "rounded-none",
};

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>((props, ref) => {
	const { className, width, height, rounded = "md", style, ...rest } = props;
	return (
		<div
			ref={ref}
			aria-hidden="true"
			className={cn("bg-surface-overlay motion-safe:animate-pulse", roundedMap[rounded], className)}
			style={{
				width,
				height,
				...style,
			}}
			{...rest}
		/>
	);
});
Skeleton.displayName = "Skeleton";
