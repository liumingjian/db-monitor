import type { ReactNode } from "react";

export type LoginErrorLevel = "inline" | "page";

export interface LoginErrorBannerProps {
	readonly level: LoginErrorLevel;
	readonly message: string;
	readonly traceId: string | null;
	readonly traceIdLabel: string;
	readonly action?: ReactNode;
}

const LEVEL_STYLES: Record<LoginErrorLevel, string> = {
	inline:
		"rounded-md border border-sev-critical-border bg-sev-critical-bg px-3 py-2 text-xs text-sev-critical",
	page: "rounded-md border border-sev-critical-border bg-sev-critical-bg px-4 py-4 text-sm text-sev-critical",
};

export function LoginErrorBanner(props: LoginErrorBannerProps) {
	const { level, message, traceId, traceIdLabel, action } = props;
	return (
		<div role="alert" aria-live="assertive" className={LEVEL_STYLES[level]}>
			<p className="font-medium leading-5">{message}</p>
			{traceId !== null ? (
				<p className="mt-1 font-mono text-[11px] tabular-nums text-fg-muted">
					{traceIdLabel}: {traceId}
				</p>
			) : null}
			{action !== undefined ? <div className="mt-3">{action}</div> : null}
		</div>
	);
}
