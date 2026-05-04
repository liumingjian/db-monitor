"use client";

import { Button, Input, Label, Skeleton } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { type FormEvent, useCallback, useState } from "react";

import { LoginErrorBanner } from "./login-error-banner";

interface LoginFormProps {
	readonly nextPath: string;
}

type SubmitState =
	| { readonly kind: "idle" }
	| { readonly kind: "submitting" }
	| {
			readonly kind: "failed";
			readonly level: "inline" | "page";
			readonly messageKey: "errorCredentials" | "errorServer" | "errorNetwork" | "errorUnexpected";
			readonly traceId: string | null;
	  };

const LOGIN_ENDPOINT = "/api/login";

function classifyFailure(status: number): {
	readonly level: "inline" | "page";
	readonly messageKey: "errorCredentials" | "errorServer" | "errorUnexpected";
} {
	if (status === 401 || status === 403 || status === 422) {
		return { level: "inline", messageKey: "errorCredentials" };
	}
	if (status >= 500) {
		return { level: "page", messageKey: "errorServer" };
	}
	return { level: "inline", messageKey: "errorUnexpected" };
}

async function extractTraceId(response: Response): Promise<string | null> {
	const contentType = response.headers.get("content-type") ?? "";
	if (!contentType.includes("application/json")) {
		return null;
	}
	try {
		const body = (await response.clone().json()) as { readonly trace_id?: unknown };
		return typeof body.trace_id === "string" && body.trace_id.length > 0 ? body.trace_id : null;
	} catch {
		return null;
	}
}

export function LoginForm({ nextPath }: LoginFormProps) {
	const t = useTranslations("loginPage");
	const [state, setState] = useState<SubmitState>({ kind: "idle" });

	const handleSubmit = useCallback(
		async (event: FormEvent<HTMLFormElement>) => {
			event.preventDefault();
			const form = event.currentTarget;
			const formData = new FormData(form);
			setState({ kind: "submitting" });
			try {
				const response = await fetch(LOGIN_ENDPOINT, {
					body: formData,
					method: "POST",
					redirect: "manual",
				});
				if (response.type === "opaqueredirect" || response.status === 303) {
					window.location.assign(nextPath);
					return;
				}
				if (response.ok) {
					window.location.assign(nextPath);
					return;
				}
				const { level, messageKey } = classifyFailure(response.status);
				const traceId = await extractTraceId(response);
				setState({ kind: "failed", level, messageKey, traceId });
			} catch {
				setState({
					kind: "failed",
					level: "page",
					messageKey: "errorNetwork",
					traceId: null,
				});
			}
		},
		[nextPath],
	);

	const retry = useCallback(() => {
		setState({ kind: "idle" });
	}, []);

	if (state.kind === "failed" && state.level === "page") {
		return (
			<div className="flex h-full w-full items-center justify-center p-6">
				<div className="w-full max-w-md">
					<LoginErrorBanner
						level="page"
						message={t(state.messageKey)}
						traceId={state.traceId}
						traceIdLabel={t("traceIdLabel")}
						action={
							<Button size="sm" variant="outline" onClick={retry} type="button">
								{t("retry")}
							</Button>
						}
					/>
				</div>
			</div>
		);
	}

	const isSubmitting = state.kind === "submitting";

	return (
		<form
			noValidate
			onSubmit={handleSubmit}
			action={LOGIN_ENDPOINT}
			method="post"
			className="flex w-full max-w-md flex-col gap-6 rounded-lg border border-border-subtle bg-bg-base p-8 shadow-[0_24px_60px_rgba(0,0,0,0.25)]"
		>
			<header className="flex flex-col gap-1">
				<h2 className="text-xl font-semibold text-fg-primary">{t("formTitle")}</h2>
				<p className="text-xs text-fg-muted">{t("formSubtitle")}</p>
			</header>
			{state.kind === "failed" && state.level === "inline" ? (
				<LoginErrorBanner
					level="inline"
					message={t(state.messageKey)}
					traceId={state.traceId}
					traceIdLabel={t("traceIdLabel")}
				/>
			) : null}
			<input name="next" type="hidden" value={nextPath} />
			{isSubmitting ? (
				<div className="flex flex-col gap-4" aria-busy="true" aria-live="polite">
					<Skeleton className="h-4 w-20" />
					<Skeleton className="h-9 w-full" />
					<Skeleton className="h-4 w-20" />
					<Skeleton className="h-9 w-full" />
					<Skeleton className="h-9 w-full" />
					<p className="text-xs text-fg-muted">{t("submitting")}</p>
				</div>
			) : (
				<div className="flex flex-col gap-4">
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="login-username" required>
							{t("username")}
						</Label>
						<Input
							id="login-username"
							name="username"
							autoComplete="username"
							required
							placeholder={t("usernamePlaceholder")}
						/>
					</div>
					<div className="flex flex-col gap-1.5">
						<Label htmlFor="login-password" required>
							{t("password")}
						</Label>
						<Input
							id="login-password"
							name="password"
							type="password"
							autoComplete="current-password"
							required
							placeholder={t("passwordPlaceholder")}
						/>
					</div>
					<Button type="submit" size="lg">
						{t("submit")}
					</Button>
				</div>
			)}
		</form>
	);
}
