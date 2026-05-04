"use client";

import { registerCommandPaletteShortcut } from "@db-monitor/ui";
import {
	type ReactNode,
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useState,
} from "react";

export interface CommandPaletteControl {
	readonly open: boolean;
	readonly setOpen: (next: boolean) => void;
	readonly toggle: () => void;
}

const CommandPaletteContext = createContext<CommandPaletteControl | null>(null);

export function useCommandPalette(): CommandPaletteControl {
	const ctx = useContext(CommandPaletteContext);
	if (!ctx) {
		throw new Error("useCommandPalette must be used within <CommandPaletteProvider>.");
	}
	return ctx;
}

export function CommandPaletteProvider(props: { readonly children: ReactNode }) {
	const [open, setOpen] = useState(false);

	const toggle = useCallback(() => setOpen((prev) => !prev), []);

	useEffect(() => {
		const unregister = registerCommandPaletteShortcut(() => setOpen((prev) => !prev));
		return () => unregister();
	}, []);

	const value = useMemo<CommandPaletteControl>(() => ({ open, setOpen, toggle }), [open, toggle]);

	return (
		<CommandPaletteContext.Provider value={value}>{props.children}</CommandPaletteContext.Provider>
	);
}
