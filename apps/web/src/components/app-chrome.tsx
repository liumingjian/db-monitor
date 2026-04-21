import type { ReactNode } from "react";

import { buildWebShellModel } from "../app-shell";
import type { SessionSnapshot } from "../auth";

interface AppChromeProps {
	readonly children: ReactNode;
	readonly session: SessionSnapshot;
}

export function AppChrome({ children, session }: AppChromeProps) {
	const shell = buildWebShellModel(session);

	return (
		<div className="min-h-screen bg-[var(--surface)] text-[var(--ink)]">
			<div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-[260px_1fr]">
				<aside className="rounded-[2rem] border border-black/10 bg-white/80 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
					<p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--accent)]">
						DB Monitor
					</p>
					<h1 className="mt-4 text-3xl font-semibold leading-tight">{shell.title}</h1>
					{shell.activeOrganization ? (
						<div className="mt-6 rounded-[1.6rem] border border-black/8 bg-[var(--panel)] p-4">
							<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
								Active organization
							</p>
							<div className="mt-3 flex items-start justify-between gap-3">
								<div>
									<p className="text-lg font-semibold text-[var(--ink)]">
										{shell.activeOrganization.name}
									</p>
									<p className="mt-1 text-sm text-[var(--muted)]">
										{shell.activeOrganization.slug}
									</p>
								</div>
								<span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
									{shell.activeOrganization.membershipCount} membership
									{shell.activeOrganization.membershipCount === 1 ? "" : "s"}
								</span>
							</div>
							<div className="mt-4 flex flex-wrap gap-2">
								{(shell.activeOrganization.roles.length === 0
									? ["no explicit roles"]
									: shell.activeOrganization.roles
								).map((role) => (
									<span
										className="rounded-full border border-black/8 bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)]"
										key={role}
									>
										{role}
									</span>
								))}
							</div>
							<p className="mt-4 text-sm leading-6 text-[var(--muted)]">
								Assets, alerts, rules, and settings in this shell are scoped to this organization.
							</p>
						</div>
					) : null}
					<nav className="mt-8 space-y-3">
						{shell.navItems.map((item) => (
							<a
								className="block rounded-[1.4rem] border border-black/5 bg-[var(--panel)] px-4 py-3 transition hover:-translate-y-0.5 hover:border-[var(--accent)] hover:bg-[var(--panel-strong)]"
								href={item.href}
								key={item.href}
							>
								<p className="text-sm font-semibold text-[var(--ink)]">{item.label}</p>
								<p className="mt-1 text-sm text-[var(--muted)]">{item.description}</p>
							</a>
						))}
					</nav>
				</aside>
				<main className="space-y-6">
					<section className="rounded-[2rem] border border-black/10 bg-[var(--panel)] p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)]">
						<div className="grid gap-4 md:grid-cols-3">
							{shell.panels.map((panel) => (
								<div
									className="rounded-[1.6rem] border border-black/5 bg-white/80 p-5"
									key={panel.href}
								>
									<p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--accent)]">
										{panel.eyebrow}
									</p>
									<h2 className="mt-3 text-xl font-semibold">{panel.title}</h2>
									<p className="mt-2 text-sm leading-6 text-[var(--muted)]">{panel.summary}</p>
								</div>
							))}
						</div>
					</section>
					<section className="rounded-[2rem] border border-black/10 bg-white/80 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
						{children}
					</section>
				</main>
			</div>
		</div>
	);
}
