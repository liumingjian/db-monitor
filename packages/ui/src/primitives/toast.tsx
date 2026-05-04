"use client";

import {
	type ReactNode,
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useRef,
	useState,
} from "react";
import { cn } from "./utils";

export type ToastVariant = "success" | "warning" | "error" | "info";

export interface ToastInput {
	readonly title: string;
	readonly description?: string;
	readonly variant?: ToastVariant;
	readonly durationMs?: number;
}

interface ToastItem extends ToastInput {
	readonly id: string;
}

interface ToastContextValue {
	readonly toast: (input: ToastInput) => string;
	readonly dismiss: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const DEFAULT_DURATION_MS = 3000;
const ERROR_DURATION_MS = 5000;

const variantStyles: Record<ToastVariant, string> = {
	success: "border-sev-ok-border bg-sev-ok-bg text-sev-ok",
	warning: "border-sev-warning-border bg-sev-warning-bg text-sev-warning",
	error: "border-sev-critical-border bg-sev-critical-bg text-sev-critical",
	info: "border-sev-info-border bg-sev-info-bg text-sev-info",
};

const resolveDuration = (input: ToastInput): number => {
	if (typeof input.durationMs === "number") {
		return input.durationMs;
	}
	return input.variant === "error" ? ERROR_DURATION_MS : DEFAULT_DURATION_MS;
};

export const ToastProvider = ({ children }: { readonly children?: ReactNode }) => {
	const [items, setItems] = useState<ReadonlyArray<ToastItem>>([]);
	const timers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

	const dismiss = useCallback((id: string) => {
		const timer = timers.current.get(id);
		if (timer) {
			clearTimeout(timer);
			timers.current.delete(id);
		}
		setItems((prev) => prev.filter((item) => item.id !== id));
	}, []);

	const toast = useCallback(
		(input: ToastInput): string => {
			const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
			const item: ToastItem = { ...input, id };
			setItems((prev) => [...prev, item]);
			const duration = resolveDuration(input);
			const timer = setTimeout(() => dismiss(id), duration);
			timers.current.set(id, timer);
			return id;
		},
		[dismiss],
	);

	useEffect(
		() => () => {
			for (const timer of timers.current.values()) {
				clearTimeout(timer);
			}
			timers.current.clear();
		},
		[],
	);

	const value = useMemo<ToastContextValue>(() => ({ toast, dismiss }), [toast, dismiss]);

	return (
		<ToastContext.Provider value={value}>
			{children}
			<div
				aria-live="polite"
				aria-atomic="true"
				className="pointer-events-none fixed right-4 top-4 z-[100] flex w-full max-w-sm flex-col gap-2"
			>
				{items.map((item) => (
					<ToastCard key={item.id} item={item} onDismiss={() => dismiss(item.id)} />
				))}
			</div>
		</ToastContext.Provider>
	);
};

const ToastCard = ({
	item,
	onDismiss,
}: {
	readonly item: ToastItem;
	readonly onDismiss: () => void;
}) => {
	const variant = item.variant ?? "info";
	return (
		<output
			className={cn(
				"pointer-events-auto rounded-md border px-4 py-3 shadow-lg backdrop-blur",
				variantStyles[variant],
			)}
		>
			<div className="flex items-start justify-between gap-3">
				<div className="flex flex-col gap-0.5">
					<p className="text-sm font-medium">{item.title}</p>
					{item.description ? <p className="text-xs opacity-90">{item.description}</p> : null}
				</div>
				<button
					type="button"
					onClick={onDismiss}
					className="text-fg-muted hover:text-fg-primary text-sm leading-none"
					aria-label="dismiss"
				>
					×
				</button>
			</div>
		</output>
	);
};

export const useToast = (): ToastContextValue => {
	const ctx = useContext(ToastContext);
	if (!ctx) {
		throw new Error("useToast must be used within <ToastProvider>.");
	}
	return ctx;
};
