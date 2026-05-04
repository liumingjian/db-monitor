"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { useEffect } from "react";

interface ErrorBoundaryProps {
	readonly error: Error & { readonly digest?: string };
	readonly reset: () => void;
}

export default function AppError({ error, reset }: ErrorBoundaryProps) {
	const tError = useTranslations("error");
	const tCommon = useTranslations("common");
	const tNav = useTranslations("nav");

	useEffect(() => {
		// eslint-disable-next-line no-console
		console.error("[app-error]", error);
	}, [error]);

	return (
		<div className="flex min-h-dvh w-full items-center justify-center bg-bg-deep p-6 text-fg-primary">
			<div className="flex w-full max-w-md flex-col items-start gap-4 rounded-lg border border-border-hairline bg-bg-elevated p-8">
				<div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-widest text-accent">
					<span className="inline-block h-2 w-2 rounded-full bg-accent" aria-hidden="true" />
					{tCommon("appName")}
				</div>
				<h1 className="text-xl font-semibold">{tError("genericTitle")}</h1>
				<p className="text-sm text-fg-secondary">{tError("genericHint")}</p>
				{error.digest ? (
					<p className="font-mono text-xs text-fg-muted">trace_id: {error.digest}</p>
				) : null}
				<div className="mt-2 flex gap-2">
					<button
						type="button"
						onClick={reset}
						className="inline-flex h-9 items-center rounded-md bg-accent px-4 text-sm font-medium text-on-accent hover:bg-accent/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
					>
						{tCommon("retry")}
					</button>
					<Link
						href="/overview"
						className="inline-flex h-9 items-center rounded-md border border-border-subtle px-4 text-sm font-medium text-fg-secondary hover:bg-surface-overlay hover:text-fg-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
					>
						{tNav("overview")}
					</Link>
				</div>
			</div>
		</div>
	);
}
