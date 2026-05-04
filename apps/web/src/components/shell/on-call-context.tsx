"use client";

import type { OnCallPermissionState } from "@db-monitor/ui";
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

import { ON_CALL_AUTO_OFF_MS, computeOnCallRemaining } from "./on-call-math";

const STORAGE_KEY = "alerts.oncall";
const AUTO_OFF_MS = ON_CALL_AUTO_OFF_MS;
const PULSE_EVENT = "alerts.oncall.pulse";
const TICK_MS = 30_000;

interface StoredState {
	readonly enabled: boolean;
	readonly enabledAt: number;
}

export interface OnCallState {
	readonly enabled: boolean;
	readonly remainingMinutes: number | null;
	readonly permission: OnCallPermissionState;
	readonly enable: () => Promise<void>;
	readonly disable: () => void;
	readonly toggle: () => Promise<void>;
}

const OnCallContext = createContext<OnCallState | null>(null);

export function useOnCall(): OnCallState {
	const ctx = useContext(OnCallContext);
	if (!ctx) {
		throw new Error("useOnCall must be used within <OnCallProvider>.");
	}
	return ctx;
}

export interface OnCallPulse {
	readonly title: string;
	readonly body?: string;
	readonly tag?: string;
}

export interface OnCallProviderProps {
	readonly children: ReactNode;
	/** Invoked when OS Notification fallback must surface a pulse in-app. */
	readonly onFallbackToast?: (pulse: OnCallPulse) => void;
}

export function OnCallProvider(props: OnCallProviderProps) {
	const { children, onFallbackToast } = props;
	const [enabled, setEnabled] = useState(false);
	const [enabledAt, setEnabledAt] = useState<number | null>(null);
	const [permission, setPermission] = useState<OnCallPermissionState>(() =>
		detectInitialPermission(),
	);
	const [now, setNow] = useState(() => Date.now());
	const fallbackRef = useRef(onFallbackToast);
	fallbackRef.current = onFallbackToast;

	// Hydrate from localStorage on mount + enforce 2h auto-off
	useEffect(() => {
		const stored = readStored();
		if (stored === null || !stored.enabled) {
			return;
		}
		const { expired } = computeOnCallRemaining(true, stored.enabledAt, Date.now(), AUTO_OFF_MS);
		if (expired) {
			clearStored();
			return;
		}
		setEnabled(true);
		setEnabledAt(stored.enabledAt);
	}, []);

	// Tick clock for remainingMinutes + auto-off enforcement
	useEffect(() => {
		if (!enabled || enabledAt === null) {
			return;
		}
		setNow(Date.now());
		const handle = window.setInterval(() => {
			setNow(Date.now());
		}, TICK_MS);
		return () => window.clearInterval(handle);
	}, [enabled, enabledAt]);

	useEffect(() => {
		if (!enabled || enabledAt === null) {
			return;
		}
		const { expired } = computeOnCallRemaining(enabled, enabledAt, now, AUTO_OFF_MS);
		if (expired) {
			clearStored();
			setEnabled(false);
			setEnabledAt(null);
		}
	}, [enabled, enabledAt, now]);

	// Cross-tab sync
	useEffect(() => {
		const onStorage = (event: StorageEvent) => {
			if (event.key !== STORAGE_KEY) {
				return;
			}
			const stored = readStored();
			if (stored === null || !stored.enabled) {
				setEnabled(false);
				setEnabledAt(null);
				return;
			}
			setEnabled(true);
			setEnabledAt(stored.enabledAt);
		};
		window.addEventListener("storage", onStorage);
		return () => window.removeEventListener("storage", onStorage);
	}, []);

	// OS Notification subscription (Q17 rule #8)
	useEffect(() => {
		if (!enabled) {
			return;
		}
		const onPulse = (event: Event) => {
			const custom = event as CustomEvent<OnCallPulse>;
			const pulse = custom.detail;
			if (!pulse) {
				return;
			}
			deliverPulse(pulse, permission, fallbackRef.current);
		};
		window.addEventListener(PULSE_EVENT, onPulse as EventListener);
		return () => window.removeEventListener(PULSE_EVENT, onPulse as EventListener);
	}, [enabled, permission]);

	const enable = useCallback(async () => {
		const nextPermission = await requestPermission();
		setPermission(nextPermission);
		const startedAt = Date.now();
		writeStored({ enabled: true, enabledAt: startedAt });
		setEnabled(true);
		setEnabledAt(startedAt);
	}, []);

	const disable = useCallback(() => {
		clearStored();
		setEnabled(false);
		setEnabledAt(null);
	}, []);

	const toggle = useCallback(async () => {
		if (enabled) {
			disable();
			return;
		}
		await enable();
	}, [enabled, enable, disable]);

	const remainingMinutes = useMemo<number | null>(() => {
		return computeOnCallRemaining(enabled, enabledAt, now).remainingMinutes;
	}, [enabled, enabledAt, now]);

	const value = useMemo<OnCallState>(
		() => ({ enabled, remainingMinutes, permission, enable, disable, toggle }),
		[enabled, remainingMinutes, permission, enable, disable, toggle],
	);

	return <OnCallContext.Provider value={value}>{children}</OnCallContext.Provider>;
}

function readStored(): StoredState | null {
	if (typeof window === "undefined") {
		return null;
	}
	try {
		const raw = window.localStorage.getItem(STORAGE_KEY);
		if (!raw) {
			return null;
		}
		const parsed = JSON.parse(raw) as Partial<StoredState>;
		if (typeof parsed.enabled !== "boolean" || typeof parsed.enabledAt !== "number") {
			return null;
		}
		return { enabled: parsed.enabled, enabledAt: parsed.enabledAt };
	} catch {
		return null;
	}
}

function writeStored(state: StoredState): void {
	if (typeof window === "undefined") {
		return;
	}
	window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function clearStored(): void {
	if (typeof window === "undefined") {
		return;
	}
	window.localStorage.removeItem(STORAGE_KEY);
}

function detectInitialPermission(): OnCallPermissionState {
	if (typeof window === "undefined" || typeof window.Notification === "undefined") {
		return "unsupported";
	}
	const current = window.Notification.permission;
	if (current === "granted" || current === "denied") {
		return current;
	}
	return "default";
}

async function requestPermission(): Promise<OnCallPermissionState> {
	if (typeof window === "undefined" || typeof window.Notification === "undefined") {
		console.warn("[on-call] OS Notification API unavailable; falling back to in-app toasts.");
		return "unsupported";
	}
	try {
		const result = await window.Notification.requestPermission();
		if (result === "granted" || result === "denied") {
			if (result === "denied") {
				console.warn("[on-call] Notification permission denied; falling back to in-app toasts.");
			}
			return result;
		}
		return "default";
	} catch (error) {
		console.warn("[on-call] Notification permission request failed:", error);
		return "denied";
	}
}

function deliverPulse(
	pulse: OnCallPulse,
	permission: OnCallPermissionState,
	fallback: OnCallProviderProps["onFallbackToast"],
): void {
	if (permission === "granted" && typeof window.Notification === "function") {
		try {
			new window.Notification(pulse.title, { body: pulse.body, tag: pulse.tag });
			return;
		} catch (error) {
			console.warn("[on-call] OS Notification creation failed, falling back to toast:", error);
		}
	}
	if (fallback) {
		fallback(pulse);
		return;
	}
	console.warn("[on-call] pulse received but no delivery channel available", pulse);
}

/**
 * Utility for Alerts page to dispatch a pulse event.
 */
export function dispatchOnCallPulse(pulse: OnCallPulse): void {
	if (typeof window === "undefined") {
		return;
	}
	window.dispatchEvent(new CustomEvent<OnCallPulse>(PULSE_EVENT, { detail: pulse }));
}

export const ON_CALL_STORAGE_KEY = STORAGE_KEY;
export { ON_CALL_AUTO_OFF_MS, computeOnCallRemaining } from "./on-call-math";
export const ON_CALL_PULSE_EVENT = PULSE_EVENT;
