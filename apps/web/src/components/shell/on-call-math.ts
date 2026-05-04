export const ON_CALL_AUTO_OFF_MS = 2 * 60 * 60 * 1000;

export interface OnCallRemaining {
	readonly expired: boolean;
	readonly remainingMs: number;
	readonly remainingMinutes: number | null;
}

/**
 * Pure helper: compute remaining auto-off milliseconds and whether the 2h
 * window has elapsed. No DOM / window dependency, safe for unit tests.
 */
export function computeOnCallRemaining(
	enabled: boolean,
	enabledAt: number | null,
	now: number,
	autoOffMs: number = ON_CALL_AUTO_OFF_MS,
): OnCallRemaining {
	if (!enabled || enabledAt === null) {
		return { expired: false, remainingMs: 0, remainingMinutes: null };
	}
	const elapsed = now - enabledAt;
	if (elapsed >= autoOffMs) {
		return { expired: true, remainingMs: 0, remainingMinutes: 0 };
	}
	const remainingMs = autoOffMs - elapsed;
	return {
		expired: false,
		remainingMs,
		remainingMinutes: Math.max(0, Math.ceil(remainingMs / 60_000)),
	};
}
