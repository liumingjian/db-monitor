"use client";

import {
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
} from "react";
import { cn } from "./utils";

const ACTIVE_DIALOG_REGISTRY = new Set<string>();

interface DialogContextValue {
	readonly open: boolean;
	readonly onClose: () => void;
	readonly titleId: string;
	readonly descriptionId: string;
}

const DialogContext = createContext<DialogContextValue | null>(null);

const useDialogContext = (): DialogContextValue => {
	const ctx = useContext(DialogContext);
	if (!ctx) {
		throw new Error("Dialog subcomponents must be used within <Dialog>.");
	}
	return ctx;
};

export interface DialogProps {
	readonly open: boolean;
	readonly onOpenChange: (next: boolean) => void;
	readonly children?: ReactNode;
}

export const Dialog = ({ open, onOpenChange, children }: DialogProps) => {
	const instanceId = useId();
	const titleId = `${instanceId}-title`;
	const descriptionId = `${instanceId}-desc`;
	const onClose = useCallback(() => onOpenChange(false), [onOpenChange]);

	useEffect(() => {
		if (!open) {
			return;
		}
		if (ACTIVE_DIALOG_REGISTRY.size > 0) {
			throw new Error("Dialog stacking is forbidden: another dialog is already open.");
		}
		ACTIVE_DIALOG_REGISTRY.add(instanceId);
		return () => {
			ACTIVE_DIALOG_REGISTRY.delete(instanceId);
		};
	}, [open, instanceId]);

	useEffect(() => {
		if (!open) {
			return;
		}
		const onKey = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				event.stopPropagation();
				onClose();
			}
		};
		document.addEventListener("keydown", onKey);
		return () => document.removeEventListener("keydown", onKey);
	}, [open, onClose]);

	const value = useMemo<DialogContextValue>(
		() => ({ open, onClose, titleId, descriptionId }),
		[open, onClose, titleId, descriptionId],
	);

	if (!open) {
		return null;
	}
	return <DialogContext.Provider value={value}>{children}</DialogContext.Provider>;
};

export const DialogOverlay = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, onClick, ...rest } = props;
		const { onClose } = useDialogContext();
		const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
			if (event.target === event.currentTarget) {
				onClose();
			}
			onClick?.(event);
		};
		return (
			<div
				ref={ref}
				onClick={handleClick}
				className={cn(
					"fixed inset-0 z-50 flex items-center justify-center bg-bg-deep/70 backdrop-blur-sm",
					className,
				)}
				{...rest}
			/>
		);
	},
);
DialogOverlay.displayName = "DialogOverlay";

export interface DialogContentProps extends HTMLAttributes<HTMLDivElement> {
	readonly children?: ReactNode;
}

export const DialogContent = forwardRef<HTMLDivElement, DialogContentProps>((props, ref) => {
	const { className, children, ...rest } = props;
	const { titleId, descriptionId } = useDialogContext();
	const contentRef = useRef<HTMLDivElement | null>(null);
	useEffect(() => {
		contentRef.current?.focus();
	}, []);
	return (
		<DialogOverlay>
			<div
				ref={(node) => {
					contentRef.current = node;
					if (typeof ref === "function") {
						ref(node);
					} else if (ref) {
						(ref as { current: HTMLDivElement | null }).current = node;
					}
				}}
				// biome-ignore lint/a11y/useSemanticElements: native <dialog> has incompatible open/close semantics; we manage overlay + focus ourselves.
				role="dialog"
				aria-modal="true"
				aria-labelledby={titleId}
				aria-describedby={descriptionId}
				tabIndex={-1}
				className={cn(
					"relative w-full max-w-lg rounded-lg border border-border-subtle bg-bg-elevated text-fg-primary shadow-xl outline-none",
					className,
				)}
				{...rest}
			>
				{children}
			</div>
		</DialogOverlay>
	);
});
DialogContent.displayName = "DialogContent";

export const DialogHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<div
				ref={ref}
				className={cn("flex flex-col gap-1.5 border-b border-border-hairline p-4", className)}
				{...rest}
			/>
		);
	},
);
DialogHeader.displayName = "DialogHeader";

export const DialogTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
	(props, ref) => {
		const { className, id, ...rest } = props;
		const { titleId } = useDialogContext();
		return (
			<h2
				ref={ref}
				id={id ?? titleId}
				className={cn("text-base font-semibold leading-6 text-fg-primary", className)}
				{...rest}
			/>
		);
	},
);
DialogTitle.displayName = "DialogTitle";

export const DialogDescription = forwardRef<
	HTMLParagraphElement,
	HTMLAttributes<HTMLParagraphElement>
>((props, ref) => {
	const { className, id, ...rest } = props;
	const { descriptionId } = useDialogContext();
	return (
		<p
			ref={ref}
			id={id ?? descriptionId}
			className={cn("text-sm text-fg-muted", className)}
			{...rest}
		/>
	);
});
DialogDescription.displayName = "DialogDescription";

export const DialogBody = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return <div ref={ref} className={cn("p-4", className)} {...rest} />;
	},
);
DialogBody.displayName = "DialogBody";

export const DialogFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
	(props, ref) => {
		const { className, ...rest } = props;
		return (
			<div
				ref={ref}
				className={cn(
					"flex items-center justify-end gap-2 border-t border-border-hairline p-4",
					className,
				)}
				{...rest}
			/>
		);
	},
);
DialogFooter.displayName = "DialogFooter";
