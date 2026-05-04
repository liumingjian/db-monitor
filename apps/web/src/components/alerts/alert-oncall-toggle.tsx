"use client";

import { Switch } from "@db-monitor/ui";
import { useEffect, useState } from "react";

const ONCALL_STORAGE_KEY = "alerts.oncall";

export function AlertOnCallToggle() {
	const [enabled, setEnabled] = useState<boolean>(false);
	const [hydrated, setHydrated] = useState<boolean>(false);

	useEffect(() => {
		try {
			const stored = window.localStorage.getItem(ONCALL_STORAGE_KEY);
			setEnabled(stored === "on");
		} finally {
			setHydrated(true);
		}
	}, []);

	const handleChange = (next: boolean) => {
		setEnabled(next);
		try {
			window.localStorage.setItem(ONCALL_STORAGE_KEY, next ? "on" : "off");
			window.dispatchEvent(new CustomEvent("alerts:oncall-change", { detail: { enabled: next } }));
		} catch {
			// localStorage unavailable (private mode, SSR edge); swallow since state already flipped.
		}
	};

	return (
		<div className="flex items-center gap-3 rounded-md border border-border-hairline bg-bg-elevated px-3 py-2">
			<div className="flex min-w-0 flex-col">
				<span className="text-xs font-semibold uppercase tracking-wider text-fg-muted">
					值班模式
				</span>
				<span className="text-sm text-fg-primary">{enabled ? "已开启" : "未开启"}</span>
			</div>
			<Switch
				aria-label="值班模式"
				checked={enabled}
				disabled={!hydrated}
				onCheckedChange={handleChange}
			/>
		</div>
	);
}
