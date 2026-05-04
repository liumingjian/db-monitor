"use client";

import { type CommandItem, CommandPalette } from "@db-monitor/ui";
import { useTranslations } from "next-intl";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { useCommandPalette } from "./command-palette-context";

interface CommandPaletteApiResponse {
	readonly items: readonly CommandItem[];
}

export function AppCommandPalette() {
	const { open, setOpen } = useCommandPalette();
	const router = useRouter();
	const t = useTranslations("commandPalette");
	const [items, setItems] = useState<readonly CommandItem[]>([]);
	const [loading, setLoading] = useState(false);
	const [loaded, setLoaded] = useState(false);

	useEffect(() => {
		if (!open || loaded || loading) {
			return;
		}
		let cancelled = false;
		setLoading(true);
		(async () => {
			try {
				const res = await fetch("/api/command-palette", {
					cache: "no-store",
					credentials: "include",
				});
				if (!res.ok) {
					throw new Error(`Command palette fetch failed: ${res.status}`);
				}
				const payload = (await res.json()) as CommandPaletteApiResponse;
				if (cancelled) {
					return;
				}
				setItems(payload.items);
				setLoaded(true);
			} catch (error) {
				console.warn("[command-palette] failed to load items:", error);
			} finally {
				if (!cancelled) {
					setLoading(false);
				}
			}
		})();
		return () => {
			cancelled = true;
		};
	}, [open, loaded, loading]);

	const onSelect = useCallback(
		(item: CommandItem) => {
			router.push(item.href);
		},
		[router],
	);

	return (
		<CommandPalette
			open={open}
			onOpenChange={setOpen}
			items={items}
			isLoading={loading && !loaded}
			onSelect={onSelect}
			strings={{
				title: t("title"),
				placeholder: t("placeholder"),
				emptyTitle: t("emptyTitle"),
				emptyHint: t("emptyHint"),
				loading: t("loading"),
				groupNav: t("groupNav"),
				groupInstance: t("groupInstance"),
				groupRule: t("groupRule"),
				hintNavigate: t("hintNavigate"),
				hintSelect: t("hintSelect"),
				hintClose: t("hintClose"),
			}}
		/>
	);
}
