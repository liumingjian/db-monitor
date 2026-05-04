import type { SlowQueryEmptyState } from "../../../../src/slow-queries-ui";

interface SlowQueryEmptyStateProps {
	readonly state: SlowQueryEmptyState;
}

export function SlowQueryEmptyStateBanner({ state }: SlowQueryEmptyStateProps) {
	return (
		<div
			className="rounded-[1.2rem] border border-dashed border-black/15 bg-white px-5 py-8 text-center"
			data-empty-reason={state.reason ?? ""}
		>
			<p className="text-sm font-semibold text-[var(--ink)]">{state.title}</p>
			<p className="mt-2 text-sm text-[var(--muted)]">{state.detail}</p>
		</div>
	);
}
