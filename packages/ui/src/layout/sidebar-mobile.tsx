"use client";

import { Menu as MenuIcon, X as XIcon } from "lucide-react";
import {
	type ReactNode,
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
} from "react";

interface SidebarMobileContextValue {
	readonly open: boolean;
	readonly toggle: () => void;
	readonly close: () => void;
	readonly openDrawer: () => void;
}

const SidebarMobileContext = createContext<SidebarMobileContextValue | null>(null);

export interface SidebarMobileProviderProps {
	readonly children: ReactNode;
}

export function SidebarMobileProvider({ children }: SidebarMobileProviderProps) {
	const [open, setOpen] = useState(false);

	const close = useCallback(() => setOpen(false), []);
	const openDrawer = useCallback(() => setOpen(true), []);
	const toggle = useCallback(() => setOpen((value) => !value), []);

	useEffect(() => {
		if (!open) {
			return;
		}
		function onKey(event: KeyboardEvent) {
			if (event.key === "Escape") {
				setOpen(false);
			}
		}
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [open]);

	const value = useMemo(
		() => ({ close, open, openDrawer, toggle }),
		[close, open, openDrawer, toggle],
	);

	return <SidebarMobileContext.Provider value={value}>{children}</SidebarMobileContext.Provider>;
}

export function useSidebarMobile(): SidebarMobileContextValue {
	const ctx = useContext(SidebarMobileContext);
	if (ctx === null) {
		// Outside a provider — return a no-op so consumers can render unconditionally.
		return { close: noop, open: false, openDrawer: noop, toggle: noop };
	}
	return ctx;
}

function noop() {
	// no-op fallback when used outside SidebarMobileProvider
}

export interface SidebarMenuButtonProps {
	readonly label: string;
	readonly className?: string;
}

/**
 * Hamburger trigger for the mobile sidebar drawer. Hidden at md+ via Tailwind
 * because the inline desktop sidebar takes over there.
 */
export function SidebarMenuButton({ label, className }: SidebarMenuButtonProps) {
	const { open, toggle } = useSidebarMobile();
	const Icon = open ? XIcon : MenuIcon;
	return (
		<button
			aria-expanded={open}
			aria-label={label}
			className={
				className ??
				"inline-flex h-9 w-9 items-center justify-center rounded-md text-fg-secondary transition-colors hover:bg-surface-overlay hover:text-fg-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring md:hidden"
			}
			onClick={toggle}
			title={label}
			type="button"
		>
			<Icon aria-hidden="true" className="h-5 w-5" />
		</button>
	);
}
