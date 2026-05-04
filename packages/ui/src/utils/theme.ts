"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export type Theme = "dark" | "light";

const THEME_STORAGE_KEY = "db-monitor:ui-theme";
const DEFAULT_THEME: Theme = "dark";
const SYSTEM_PREFERS_DARK_QUERY = "(prefers-color-scheme: dark)";

export interface UseThemeResult {
	readonly theme: Theme;
	readonly setTheme: (theme: Theme) => void;
	readonly toggleTheme: () => void;
}

function readStoredTheme(): Theme | null {
	if (typeof window === "undefined") {
		return null;
	}
	const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
	if (stored === "dark" || stored === "light") {
		return stored;
	}
	return null;
}

function applyThemeToDocument(theme: Theme): void {
	if (typeof document === "undefined") {
		return;
	}
	document.documentElement.dataset.theme = theme;
}

export function useTheme(): UseThemeResult {
	const [theme, setThemeState] = useState<Theme>(DEFAULT_THEME);
	const userOverriddenRef = useRef<boolean>(false);

	useEffect(() => {
		const stored = readStoredTheme();
		if (stored) {
			userOverriddenRef.current = true;
			setThemeState(stored);
			applyThemeToDocument(stored);
			return;
		}
		applyThemeToDocument(DEFAULT_THEME);
	}, []);

	useEffect(() => {
		if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
			return;
		}
		const media = window.matchMedia(SYSTEM_PREFERS_DARK_QUERY);
		const handleChange = (event: MediaQueryListEvent): void => {
			if (userOverriddenRef.current) {
				return;
			}
			const next: Theme = event.matches ? "dark" : "light";
			setThemeState(next);
			applyThemeToDocument(next);
		};
		media.addEventListener("change", handleChange);
		return () => {
			media.removeEventListener("change", handleChange);
		};
	}, []);

	const setTheme = useCallback((next: Theme): void => {
		userOverriddenRef.current = true;
		setThemeState(next);
		applyThemeToDocument(next);
		if (typeof window !== "undefined") {
			window.localStorage.setItem(THEME_STORAGE_KEY, next);
		}
	}, []);

	const toggleTheme = useCallback((): void => {
		setThemeState((current) => {
			const next: Theme = current === "dark" ? "light" : "dark";
			userOverriddenRef.current = true;
			applyThemeToDocument(next);
			if (typeof window !== "undefined") {
				window.localStorage.setItem(THEME_STORAGE_KEY, next);
			}
			return next;
		});
	}, []);

	return { setTheme, theme, toggleTheme };
}
