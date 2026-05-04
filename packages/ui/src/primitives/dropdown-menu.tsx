"use client";

import {
	type ButtonHTMLAttributes,
	type HTMLAttributes,
	type ReactNode,
	createContext,
	forwardRef,
	useCallback,
	useContext,
	useEffect,
	useId,
	useMemo,
	useRef,
	useState,
} from "react";
import { cn } from "./utils";

interface DropdownContextValue {
	readonly open: boolean;
	readonly setOpen: (next: boolean) => void;
	readonly triggerRef: React.MutableRefObject<HTMLButtonElement | null>;
	readonly contentRef: React.MutableRefObject<HTMLDivElement | null>;
	readonly menuId: string;
}

const DropdownContext = createContext<DropdownContextValue | null>(null);

const useDropdownContext = (): DropdownContextValue => {
	const ctx = useContext(DropdownContext);
	if (!ctx) {
		throw new Error("DropdownMenu subcomponents must be used within <DropdownMenu>.");
	}
	return ctx;
};

export interface DropdownMenuProps {
	readonly children?: ReactNode;
	readonly defaultOpen?: boolean;
	readonly open?: boolean;
	readonly onOpenChange?: (next: boolean) => void;
}

export const DropdownMenu = ({
	children,
	defaultOpen = false,
	open: openProp,
	onOpenChange,
}: DropdownMenuProps) => {
	const [uncontrolled, setUncontrolled] = useState(defaultOpen);
	const isControlled = typeof openProp === "boolean";
	const open = isControlled ? openProp : uncontrolled;
	const triggerRef = useRef<HTMLButtonElement | null>(null);
	const contentRef = useRef<HTMLDivElement | null>(null);
	const menuId = useId();

	const setOpen = useCallback(
		(next: boolean) => {
			if (!isControlled) {
				setUncontrolled(next);
			}
			onOpenChange?.(next);
		},
		[isControlled, onOpenChange],
	);

	useEffect(() => {
		if (!open) {
			return;
		}
		const onDown = (event: MouseEvent) => {
			const target = event.target as Node | null;
			if (
				target &&
				!contentRef.current?.contains(target) &&
				!triggerRef.current?.contains(target)
			) {
				setOpen(false);
			}
		};
		const onKey = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				setOpen(false);
				triggerRef.current?.focus();
			}
		};
		document.addEventListener("mousedown", onDown);
		document.addEventListener("keydown", onKey);
		return () => {
			document.removeEventListener("mousedown", onDown);
			document.removeEventListener("keydown", onKey);
		};
	}, [open, setOpen]);

	const value = useMemo<DropdownContextValue>(
		() => ({ open, setOpen, triggerRef, contentRef, menuId }),
		[open, setOpen, menuId],
	);

	return (
		<DropdownContext.Provider value={value}>
			<div className="relative inline-block">{children}</div>
		</DropdownContext.Provider>
	);
};

export const DropdownMenuTrigger = forwardRef<
	HTMLButtonElement,
	ButtonHTMLAttributes<HTMLButtonElement>
>((props, ref) => {
	const { open, setOpen, triggerRef, menuId } = useDropdownContext();
	const { onClick, className, ...rest } = props;
	return (
		<button
			type="button"
			ref={(node) => {
				triggerRef.current = node;
				if (typeof ref === "function") {
					ref(node);
				} else if (ref) {
					(ref as { current: HTMLButtonElement | null }).current = node;
				}
			}}
			aria-haspopup="menu"
			aria-expanded={open}
			aria-controls={menuId}
			onClick={(event) => {
				setOpen(!open);
				onClick?.(event);
			}}
			className={cn(
				"inline-flex items-center gap-1 rounded-md border border-border-subtle bg-bg-elevated px-3 py-1.5 text-sm text-fg-primary hover:bg-surface-overlay",
				className,
			)}
			{...rest}
		/>
	);
});
DropdownMenuTrigger.displayName = "DropdownMenuTrigger";

const focusableItemSelector = "[role='menuitem']:not([aria-disabled='true']):not([data-disabled])";

export const DropdownMenuContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { open, contentRef, menuId } = useDropdownContext();
		const { className, onKeyDown, children, ...rest } = props;

		const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
			const items = Array.from(
				contentRef.current?.querySelectorAll<HTMLElement>(focusableItemSelector) ?? [],
			);
			if (items.length === 0) {
				onKeyDown?.(event);
				return;
			}
			const currentIndex = items.findIndex((item) => item === document.activeElement);
			if (event.key === "ArrowDown") {
				event.preventDefault();
				const next = items[(currentIndex + 1) % items.length];
				next?.focus();
			} else if (event.key === "ArrowUp") {
				event.preventDefault();
				const prev = items[(currentIndex - 1 + items.length) % items.length];
				prev?.focus();
			} else if (event.key === "Home") {
				event.preventDefault();
				items[0]?.focus();
			} else if (event.key === "End") {
				event.preventDefault();
				items[items.length - 1]?.focus();
			}
			onKeyDown?.(event);
		};

		if (!open) {
			return null;
		}
		return (
			<div
				ref={(node) => {
					contentRef.current = node;
					if (typeof ref === "function") {
						ref(node);
					} else if (ref) {
						(ref as { current: HTMLDivElement | null }).current = node;
					}
				}}
				role="menu"
				id={menuId}
				onKeyDown={handleKeyDown}
				className={cn(
					"absolute z-50 mt-1 min-w-[10rem] rounded-md border border-border-subtle bg-bg-elevated p-1 text-fg-primary shadow-lg outline-none",
					className,
				)}
				{...rest}
			>
				{children}
			</div>
		);
	},
);
DropdownMenuContent.displayName = "DropdownMenuContent";

export interface DropdownMenuItemProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	readonly inset?: boolean;
}

export const DropdownMenuItem = forwardRef<HTMLButtonElement, DropdownMenuItemProps>(
	(props, ref) => {
		const { setOpen } = useDropdownContext();
		const { className, onClick, disabled, inset, ...rest } = props;
		return (
			<button
				type="button"
				ref={ref}
				role="menuitem"
				tabIndex={-1}
				aria-disabled={disabled || undefined}
				data-disabled={disabled || undefined}
				onClick={(event) => {
					if (disabled) {
						return;
					}
					onClick?.(event);
					setOpen(false);
				}}
				className={cn(
					"flex w-full cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-fg-primary hover:bg-surface-overlay focus:bg-surface-overlay outline-none",
					inset && "pl-8",
					disabled && "cursor-not-allowed opacity-50",
					className,
				)}
				{...rest}
			/>
		);
	},
);
DropdownMenuItem.displayName = "DropdownMenuItem";

export const DropdownMenuLabel = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<div
				ref={ref}
				className={cn(
					"px-2 py-1.5 text-xs font-semibold uppercase tracking-wide text-fg-muted",
					className,
				)}
				{...rest}
			/>
		);
	},
);
DropdownMenuLabel.displayName = "DropdownMenuLabel";

export const DropdownMenuSeparator = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<div
				ref={ref}
				role="separator"
				tabIndex={-1}
				aria-orientation="horizontal"
				className={cn("my-1 h-px bg-border-hairline", className)}
				{...rest}
			/>
		);
	},
);
DropdownMenuSeparator.displayName = "DropdownMenuSeparator";
