"use client";

import { useCallback, useEffect, useState } from "react";

export type Density = "compact" | "comfortable" | "spacious";

const DENSITY_STORAGE_KEY = "db-monitor:ui-density";
const DEFAULT_DENSITY: Density = "comfortable";

const ROW_HEIGHT_PX: Readonly<Record<Density, number>> = {
	comfortable: 44,
	compact: 36,
	spacious: 56,
};

export interface UseDensityResult {
	readonly density: Density;
	readonly rowHeight: number;
	readonly setDensity: (density: Density) => void;
}

function isDensity(value: unknown): value is Density {
	return value === "compact" || value === "comfortable" || value === "spacious";
}

function readStoredDensity(): Density | null {
	if (typeof window === "undefined") {
		return null;
	}
	const stored = window.localStorage.getItem(DENSITY_STORAGE_KEY);
	return isDensity(stored) ? stored : null;
}

export function useDensity(): UseDensityResult {
	const [density, setDensityState] = useState<Density>(DEFAULT_DENSITY);

	useEffect(() => {
		const stored = readStoredDensity();
		if (stored) {
			setDensityState(stored);
		}
	}, []);

	const setDensity = useCallback((next: Density): void => {
		setDensityState(next);
		if (typeof window !== "undefined") {
			window.localStorage.setItem(DENSITY_STORAGE_KEY, next);
		}
	}, []);

	return { density, rowHeight: ROW_HEIGHT_PX[density], setDensity };
}
