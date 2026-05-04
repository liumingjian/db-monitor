"use client";

import {
	type ButtonHTMLAttributes,
	type HTMLAttributes,
	type ReactNode,
	createContext,
	forwardRef,
	useCallback,
	useContext,
	useMemo,
	useState,
} from "react";
import { cn } from "./utils";

interface TabsContextValue {
	readonly value: string;
	readonly setValue: (next: string) => void;
	readonly idBase: string;
}

const TabsContext = createContext<TabsContextValue | null>(null);

const useTabsContext = (): TabsContextValue => {
	const ctx = useContext(TabsContext);
	if (!ctx) {
		throw new Error("Tabs subcomponents must be used within <Tabs>.");
	}
	return ctx;
};

export interface TabsProps extends HTMLAttributes<HTMLDivElement> {
	readonly defaultValue?: string;
	readonly value?: string;
	readonly onValueChange?: (next: string) => void;
	readonly idBase?: string;
	readonly children?: ReactNode;
}

export const Tabs = forwardRef<HTMLDivElement, TabsProps>((props, ref) => {
	const {
		defaultValue,
		value: valueProp,
		onValueChange,
		idBase = "tabs",
		className,
		children,
		...rest
	} = props;
	const [uncontrolled, setUncontrolled] = useState<string>(defaultValue ?? "");
	const isControlled = typeof valueProp === "string";
	const value = isControlled ? valueProp : uncontrolled;

	const setValue = useCallback(
		(next: string) => {
			if (!isControlled) {
				setUncontrolled(next);
			}
			onValueChange?.(next);
		},
		[isControlled, onValueChange],
	);

	const ctx = useMemo<TabsContextValue>(
		() => ({ value, setValue, idBase }),
		[value, setValue, idBase],
	);

	return (
		<TabsContext.Provider value={ctx}>
			<div ref={ref} className={cn("w-full", className)} {...rest}>
				{children}
			</div>
		</TabsContext.Provider>
	);
});
Tabs.displayName = "Tabs";

export const TabsList = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>((props, ref) => {
	const { className, ...rest } = props;
	return (
		<div
			ref={ref}
			role="tablist"
			className={cn(
				"inline-flex h-11 items-center gap-1 border-b border-border-hairline",
				className,
			)}
			{...rest}
		/>
	);
});
TabsList.displayName = "TabsList";

export interface TabsTriggerProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	readonly value: string;
}

export const TabsTrigger = forwardRef<HTMLButtonElement, TabsTriggerProps>((props, ref) => {
	const { className, value, onClick, children, ...rest } = props;
	const { value: active, setValue, idBase } = useTabsContext();
	const isActive = active === value;
	return (
		<button
			type="button"
			ref={ref}
			role="tab"
			id={`${idBase}-trigger-${value}`}
			aria-selected={isActive}
			aria-controls={`${idBase}-panel-${value}`}
			tabIndex={isActive ? 0 : -1}
			onClick={(event) => {
				setValue(value);
				onClick?.(event);
			}}
			className={cn(
				"inline-flex h-11 items-center border-b-2 px-3 text-sm font-medium transition-colors",
				isActive
					? "border-accent text-fg-primary"
					: "border-transparent text-fg-muted hover:text-fg-primary",
				className,
			)}
			{...rest}
		>
			{children}
		</button>
	);
});
TabsTrigger.displayName = "TabsTrigger";

export interface TabsContentProps extends HTMLAttributes<HTMLDivElement> {
	readonly value: string;
}

export const TabsContent = forwardRef<HTMLDivElement, TabsContentProps>((props, ref) => {
	const { className, value, children, ...rest } = props;
	const { value: active, idBase } = useTabsContext();
	if (active !== value) {
		return null;
	}
	return (
		<div
			ref={ref}
			role="tabpanel"
			id={`${idBase}-panel-${value}`}
			aria-labelledby={`${idBase}-trigger-${value}`}
			className={cn("mt-2 outline-none", className)}
			{...rest}
		>
			{children}
		</div>
	);
});
TabsContent.displayName = "TabsContent";
