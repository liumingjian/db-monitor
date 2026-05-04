"use client";

import { Moon as MoonIcon, Sun as SunIcon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { cn } from "./utils";

type Theme = "dark" | "light";

const STORAGE_KEY = "db-monitor:ui-theme";
const DEFAULT_THEME: Theme = "dark";

export interface ThemeToggleProps {
	readonly labelDark: string;
	readonly labelLight: string;
	readonly className?: string;
}

function readStoredTheme(): Theme {
	if (typeof document === "undefined") {
		return DEFAULT_THEME;
	}
	const attr = document.documentElement.dataset.theme;
	if (attr === "dark" || attr === "light") {
		return attr;
	}
	try {
		const stored = window.localStorage.getItem(STORAGE_KEY);
		if (stored === "dark" || stored === "light") {
			return stored;
		}
	} catch {
		// localStorage may be unavailable (privacy mode); fall back silently.
	}
	return DEFAULT_THEME;
}

function applyTheme(theme: Theme): void {
	if (typeof document === "undefined") {
		return;
	}
	document.documentElement.dataset.theme = theme;
	try {
		window.localStorage.setItem(STORAGE_KEY, theme);
	} catch {
		// Ignore storage failures; theme still applied to DOM.
	}
}

export function ThemeToggle(props: ThemeToggleProps) {
	const { labelDark, labelLight, className } = props;
	const [theme, setTheme] = useState<Theme>(DEFAULT_THEME);
	const [mounted, setMounted] = useState(false);

	useEffect(() => {
		setMounted(true);
		setTheme(readStoredTheme());
	}, []);

	const toggle = useCallback(() => {
		setTheme((current) => {
			const next: Theme = current === "dark" ? "light" : "dark";
			applyTheme(next);
			return next;
		});
	}, []);

	const isDark = theme === "dark";
	const label = isDark ? labelLight : labelDark;

	return (
		<button
			type="button"
			onClick={toggle}
			aria-label={label}
			title={label}
			suppressHydrationWarning
			className={cn(
				"inline-flex h-8 w-8 items-center justify-center rounded-md",
				"text-fg-secondary transition-colors hover:text-fg-primary hover:bg-surface-overlay",
				"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
				className,
			)}
		>
			{mounted && isDark ? (
				<SunIcon className="h-4 w-4" aria-hidden="true" />
			) : (
				<MoonIcon className="h-4 w-4" aria-hidden="true" />
			)}
		</button>
	);
}
