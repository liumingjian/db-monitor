"use client";

import { useEffect, useRef } from "react";

const DEFAULT_INTERVAL_MS = 30_000;

export interface UseAutoRefreshOptions {
	readonly intervalMs?: number;
	readonly paused?: boolean;
}

/**
 * Schedule `callback` to run every `intervalMs` while mounted and not paused.
 * Uses a ref to keep the callback reference stable across renders, avoiding stale closures.
 */
export function useAutoRefresh(callback: () => void, options: UseAutoRefreshOptions = {}): void {
	const { intervalMs = DEFAULT_INTERVAL_MS, paused = false } = options;
	const callbackRef = useRef<() => void>(callback);

	useEffect(() => {
		callbackRef.current = callback;
	}, [callback]);

	useEffect(() => {
		if (paused || intervalMs <= 0) {
			return;
		}
		const handle = setInterval(() => {
			callbackRef.current();
		}, intervalMs);
		return () => {
			clearInterval(handle);
		};
	}, [intervalMs, paused]);
}
