import type { ManagedUserResponse, RoleCatalogEntryResponse } from "@db-monitor/api-client";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	Label,
} from "@db-monitor/ui";

import { updateUserRolesAction } from "../../monitoring-actions";

export interface UserRoleCardProps {
	readonly user: ManagedUserResponse;
	readonly roleCatalog: readonly RoleCatalogEntryResponse[];
	readonly labels: {
		readonly activeOrg: string;
		readonly permissions: string;
		readonly noPermissions: string;
		readonly updateRoles: string;
	};
}

export function UserRoleCard(props: UserRoleCardProps) {
	const { user, roleCatalog, labels } = props;
	return (
		<Card>
			<CardHeader>
				<div className="flex items-start justify-between gap-3">
					<div className="flex flex-col gap-1">
						<CardTitle>{user.display_name}</CardTitle>
						<CardDescription className="font-mono text-xs">@{user.username}</CardDescription>
					</div>
					<div className="text-right text-xs text-fg-muted">
						<p>{labels.activeOrg}</p>
						<p className="mt-0.5 font-mono tabular-nums text-fg-secondary">
							{user.active_organization_id}
						</p>
					</div>
				</div>
			</CardHeader>
			<CardContent>
				<div className="flex flex-col gap-3">
					<div className="flex flex-col gap-1.5">
						<Label>{labels.permissions}</Label>
						<div className="flex flex-wrap gap-1.5">
							{user.effective_permissions.length === 0 ? (
								<Badge variant="outline" size="sm">
									{labels.noPermissions}
								</Badge>
							) : (
								user.effective_permissions.map((permission) => (
									<Badge key={permission} variant="secondary" size="sm">
										{permission}
									</Badge>
								))
							)}
						</div>
					</div>

					<form action={updateUserRolesAction} className="flex flex-col gap-3">
						<input name="user_id" type="hidden" value={user.user_id} />
						<div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3">
							{roleCatalog.map((entry) => (
								<label
									key={`${user.user_id}-${entry.role}`}
									className="flex cursor-pointer items-start gap-2 rounded-md border border-border-hairline bg-bg-base p-3 text-sm text-fg-primary hover:border-border-subtle"
								>
									<input
										defaultChecked={user.roles.includes(entry.role)}
										name="roles"
										type="checkbox"
										value={entry.role}
										className="mt-0.5 h-4 w-4"
									/>
									<div className="flex flex-col gap-1">
										<span className="font-medium capitalize">{entry.role}</span>
										<span className="text-xs text-fg-muted">{entry.permissions.join(", ")}</span>
									</div>
								</label>
							))}
						</div>
						<Button type="submit" variant="default" size="sm" className="self-start">
							{labels.updateRoles}
						</Button>
					</form>
				</div>
			</CardContent>
		</Card>
	);
}
