"use client";

import "./globals.css";

import { useEffect } from "react";

interface GlobalErrorProps {
	readonly error: Error & { readonly digest?: string };
	readonly reset: () => void;
}

/**
 * Last-resort fallback used when the root layout itself fails to render.
 * Cannot use next-intl here (provider is mounted in RootLayout), so the copy
 * is hard-coded to keep this file dependency-free.
 */
export default function GlobalError({ error, reset }: GlobalErrorProps) {
	useEffect(() => {
		// eslint-disable-next-line no-console
		console.error("[global-error]", error);
	}, [error]);

	return (
		<html lang="zh-CN" data-theme="dark">
			<body
				style={{
					alignItems: "center",
					backgroundColor: "var(--bg-deep)",
					color: "var(--fg-primary)",
					display: "flex",
					fontFamily: "var(--font-sans)",
					justifyContent: "center",
					minHeight: "100vh",
					padding: "1.5rem",
				}}
			>
				<div
					style={{
						background: "var(--bg-elevated)",
						border: "1px solid var(--border-hairline)",
						borderRadius: "0.5rem",
						display: "flex",
						flexDirection: "column",
						gap: "1rem",
						maxWidth: "28rem",
						padding: "2rem",
						width: "100%",
					}}
				>
					<div
						style={{
							color: "var(--accent)",
							fontSize: "0.875rem",
							fontWeight: 600,
							letterSpacing: "0.1em",
							textTransform: "uppercase",
						}}
					>
						DB Monitor
					</div>
					<h1 style={{ fontSize: "1.25rem", fontWeight: 600, margin: 0 }}>系统异常</h1>
					<p style={{ color: "var(--fg-secondary)", fontSize: "0.875rem", margin: 0 }}>
						界面外壳加载失败，请刷新或联系管理员。
					</p>
					{error.digest ? (
						<p
							style={{
								color: "var(--fg-muted)",
								fontFamily: "var(--font-mono)",
								fontSize: "0.75rem",
								margin: 0,
							}}
						>
							trace_id: {error.digest}
						</p>
					) : null}
					<button
						type="button"
						onClick={reset}
						style={{
							background: "var(--accent)",
							border: "none",
							borderRadius: "0.375rem",
							color: "var(--on-accent)",
							cursor: "pointer",
							fontSize: "0.875rem",
							fontWeight: 500,
							height: "2.25rem",
							padding: "0 1rem",
							width: "fit-content",
						}}
					>
						重试
					</button>
				</div>
			</body>
		</html>
	);
}
