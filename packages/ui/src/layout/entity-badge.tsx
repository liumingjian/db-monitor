import type { SeverityTone } from "./types";
import { cn } from "./utils";

export interface EntityBadgeProps {
	readonly tone: SeverityTone;
	readonly label: string;
	readonly className?: string;
}

const TONE_STYLES: Record<
	SeverityTone,
	{ readonly dot: string; readonly text: string; readonly border: string }
> = {
	critical: {
		dot: "bg-sev-critical",
		text: "text-sev-critical",
		border: "border-sev-critical-border",
	},
	warning: {
		dot: "bg-sev-warning",
		text: "text-sev-warning",
		border: "border-sev-warning-border",
	},
	info: {
		dot: "bg-sev-info",
		text: "text-sev-info",
		border: "border-sev-info-border",
	},
	ok: {
		dot: "bg-sev-ok",
		text: "text-sev-ok",
		border: "border-sev-ok-border",
	},
};

/**
 * 4-tone severity badge: colored dot + label, matching ADR-0012 severity axis.
 */
export function EntityBadge(props: EntityBadgeProps) {
	const { tone, label, className } = props;
	const styles = TONE_STYLES[tone];

	return (
		<span
			className={cn(
				"inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5",
				"text-xs font-medium bg-bg-elevated",
				styles.border,
				styles.text,
				className,
			)}
		>
			<span
				aria-hidden="true"
				className={cn("inline-block h-1.5 w-1.5 rounded-full", styles.dot)}
			/>
			{label}
		</span>
	);
}
