"use client";

import {
	Children,
	type ReactElement,
	type ReactNode,
	cloneElement,
	isValidElement,
	useId,
	useRef,
	useState,
} from "react";
import { cn } from "./utils";

const HOVER_DELAY_MS = 200;

export interface TooltipProps {
	readonly content: ReactNode;
	readonly children: ReactNode;
	readonly side?: "top" | "bottom" | "left" | "right";
	readonly className?: string;
}

const sidePosition: Record<NonNullable<TooltipProps["side"]>, string> = {
	top: "-top-1 left-1/2 -translate-x-1/2 -translate-y-full",
	bottom: "-bottom-1 left-1/2 -translate-x-1/2 translate-y-full",
	left: "top-1/2 -left-1 -translate-x-full -translate-y-1/2",
	right: "top-1/2 -right-1 translate-x-full -translate-y-1/2",
};

export const Tooltip = ({ content, children, side = "top", className }: TooltipProps) => {
	const [open, setOpen] = useState(false);
	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const tooltipId = useId();

	const scheduleOpen = () => {
		if (timerRef.current) {
			clearTimeout(timerRef.current);
		}
		timerRef.current = setTimeout(() => setOpen(true), HOVER_DELAY_MS);
	};

	const cancel = () => {
		if (timerRef.current) {
			clearTimeout(timerRef.current);
			timerRef.current = null;
		}
		setOpen(false);
	};

	const child = isValidElement(children)
		? (Children.only(children) as ReactElement<Record<string, unknown>>)
		: null;

	if (!child) {
		return null;
	}

	const triggerProps: Record<string, unknown> = {
		"aria-describedby": open ? tooltipId : undefined,
		onMouseEnter: scheduleOpen,
		onMouseLeave: cancel,
		onFocus: scheduleOpen,
		onBlur: cancel,
	};

	return (
		<span className="relative inline-flex">
			{cloneElement(child, triggerProps)}
			{open ? (
				<span
					id={tooltipId}
					role="tooltip"
					className={cn(
						"pointer-events-none absolute z-50 rounded-sm border border-border-subtle bg-bg-deep px-2 py-1 text-xs text-fg-primary shadow-md whitespace-nowrap",
						sidePosition[side],
						className,
					)}
				>
					{content}
				</span>
			) : null}
		</span>
	);
};
Tooltip.displayName = "Tooltip";
