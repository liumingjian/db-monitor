import { AppChrome } from "../../src/components/app-chrome";
import { resolveActiveMembership } from "../../src/auth";
import { updateSettingAction } from "../../src/monitoring-actions";
import { buildOperationsModel } from "../../src/monitoring-ui";
import { createServerApiClient, requireServerSession } from "../../src/server-api";

export default async function SettingsPage() {
	const session = await requireServerSession("/settings");
	const activeMembership = resolveActiveMembership(session);
	const apiClient = await createServerApiClient();
	const model = buildOperationsModel({
		settings: await apiClient.listSettings(),
	});

	return (
		<AppChrome session={session}>
			<div className="space-y-6">
				<div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
					<section
						className="rounded-[1.6rem] border border-black/5 bg-[var(--panel)] p-5"
						id="organization-governance"
					>
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Organization governance
						</p>
						<h2 className="mt-3 text-2xl font-semibold">
							{session.activeOrganization?.name ?? "Organization not resolved"}
						</h2>
						<p className="mt-2 text-sm text-[var(--muted)]">
							Slug {session.activeOrganization?.slug ?? "n/a"}
						</p>
						<p className="mt-4 text-sm leading-6 text-[var(--muted)]">
							This shell is pinned to the active organization returned by session auth. Asset,
							alert, rule, and setting operations stay inside this scope.
						</p>
						<div className="mt-4 flex flex-wrap gap-2">
							{(activeMembership?.roles.length ?? 0) > 0 ? (
								activeMembership?.roles.map((role) => (
									<span
										className="rounded-full border border-black/8 bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)]"
										key={role}
									>
										{role}
									</span>
								))
							) : (
								<span className="rounded-full border border-black/8 bg-white px-3 py-1 text-xs font-semibold text-[var(--ink)]">
									no explicit roles
								</span>
							)}
						</div>
					</section>
					<section className="rounded-[1.6rem] border border-black/5 bg-white p-5">
						<p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--accent)]">
							Membership scope
						</p>
						<div className="mt-4 space-y-3">
							{session.organizationMemberships.map((membership) => {
								const isActive =
									membership.organization.organization_id ===
									session.activeOrganization?.organization_id;
								return (
									<div
										className="rounded-[1.2rem] border px-4 py-4"
										key={membership.organization.organization_id}
										style={{
											backgroundColor: isActive
												? "rgba(230, 237, 232, 0.7)"
												: "rgba(255, 255, 255, 0.85)",
											borderColor: isActive
												? "rgba(74, 110, 89, 0.18)"
												: "rgba(15, 23, 42, 0.08)",
										}}
									>
										<div className="flex items-start justify-between gap-3">
											<div>
												<p className="font-semibold">{membership.organization.name}</p>
												<p className="mt-1 text-sm text-[var(--muted)]">
													{membership.organization.slug}
												</p>
											</div>
											{isActive ? (
												<span className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--accent)]">
													Active
												</span>
											) : null}
										</div>
										<p className="mt-3 text-sm text-[var(--muted)]">
											Roles: {membership.roles.join(", ")}
										</p>
									</div>
								);
							})}
						</div>
					</section>
				</div>
				<div className="space-y-4">
					<h2 className="text-2xl font-semibold">System settings</h2>
					{model.settings.map((setting) => (
						<form action={updateSettingAction} className="grid gap-2" key={setting.key}>
							<input name="key" type="hidden" value={setting.key} />
							<label className="grid gap-2" htmlFor={setting.key}>
								<span className="text-sm font-medium">{setting.key}</span>
								<input
									className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3"
									defaultValue={setting.value}
									id={setting.key}
									name="value"
								/>
							</label>
							<p className="text-sm text-[var(--muted)]">Updated at {setting.updated_at}</p>
							<button
								className="w-fit rounded-[1rem] bg-[var(--accent)] px-4 py-2 text-sm font-semibold text-white"
								type="submit"
							>
								Save setting
							</button>
						</form>
					))}
				</div>
			</div>
		</AppChrome>
	);
}
