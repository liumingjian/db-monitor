import type { SystemSettingResponse } from "@db-monitor/api-client";
import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	Input,
	Label,
} from "@db-monitor/ui";

import { updateSettingAction } from "../../monitoring-actions";

export interface SettingsKeyValueFormProps {
	readonly setting: SystemSettingResponse;
	readonly canWrite: boolean;
	readonly labels: {
		readonly keyLabel: string;
		readonly valueLabel: string;
		readonly updatedAt: string;
		readonly save: string;
		readonly permissionDenied: string;
	};
}

export function SettingsKeyValueForm(props: SettingsKeyValueFormProps) {
	const { setting, canWrite, labels } = props;
	const inputId = `setting-${setting.key}`;

	return (
		<Card>
			<CardHeader>
				<CardTitle className="font-mono text-sm">{setting.key}</CardTitle>
				<CardDescription>
					{labels.updatedAt} <span className="font-mono tabular-nums">{setting.updated_at}</span>
				</CardDescription>
			</CardHeader>
			<CardContent>
				{canWrite ? (
					<form action={updateSettingAction} className="flex flex-col gap-3">
						<input name="key" type="hidden" value={setting.key} />
						<div className="flex flex-col gap-1.5">
							<Label htmlFor={inputId}>{labels.valueLabel}</Label>
							<Input defaultValue={setting.value} id={inputId} name="value" />
						</div>
						<Button type="submit" variant="default" size="sm" className="self-start">
							{labels.save}
						</Button>
					</form>
				) : (
					<div className="flex flex-col gap-2">
						<Label>{labels.valueLabel}</Label>
						<div className="rounded-md border border-border-hairline bg-bg-base px-3 py-2 font-mono text-sm tabular-nums text-fg-secondary">
							{setting.value}
						</div>
						<p className="text-xs text-fg-muted">{labels.permissionDenied}</p>
					</div>
				)}
			</CardContent>
		</Card>
	);
}
