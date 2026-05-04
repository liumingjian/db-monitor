"use client";

import { Button } from "@db-monitor/ui";
import { DatabaseZap as DatabaseIcon, Filter as FilterIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";

interface InstancesEmptyStateProps {
	readonly reason: "first-run" | "filtered";
	readonly onOpenCreate: () => void;
}

/**
 * 双态空态：
 * - `first-run`: 组织尚未接入任何实例 → 引导新建（主 CTA）+ 文档链接占位
 * - `filtered`: 当前过滤条件导致 0 行 → 提供"清除过滤"按钮
 */
export function InstancesEmptyState(props: InstancesEmptyStateProps) {
	const { reason, onOpenCreate } = props;
	const t = useTranslations("instancesPage");
	const router = useRouter();
	const pathname = usePathname();
	const searchParams = useSearchParams();

	const clearFilters = useCallback(() => {
		const next = new URLSearchParams(searchParams?.toString() ?? "");
		for (const key of ["name", "environment", "label", "status"] as const) {
			next.delete(key);
		}
		const query = next.toString();
		router.push(query.length === 0 ? pathname : `${pathname}?${query}`);
	}, [pathname, router, searchParams]);

	if (reason === "first-run") {
		return (
			<div className="flex flex-col items-center justify-center gap-4 rounded-lg border border-dashed border-border-subtle bg-bg-base px-6 py-12 text-center">
				<DatabaseIcon aria-hidden="true" className="h-10 w-10 text-accent" />
				<div className="flex flex-col items-center gap-1">
					<h3 className="text-lg font-semibold text-fg-primary">{t("emptyFirstRunTitle")}</h3>
					<p className="max-w-md text-sm text-fg-muted">{t("emptyFirstRunDescription")}</p>
				</div>
				<div className="flex flex-wrap items-center justify-center gap-2">
					<Button onClick={onOpenCreate} type="button" variant="default">
						{t("emptyFirstRunCta")}
					</Button>
					<Link
						className="inline-flex h-9 items-center rounded-md border border-border-subtle px-4 text-sm font-medium text-fg-primary hover:bg-surface-overlay"
						href="#docs-coming-soon"
					>
						{t("emptyFirstRunDocsLink")}
					</Link>
				</div>
				<p className="font-mono text-[11px] text-fg-muted">{t("emptyFirstRunDocsHint")}</p>
			</div>
		);
	}

	return (
		<div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border-subtle bg-bg-base px-6 py-10 text-center">
			<FilterIcon aria-hidden="true" className="h-8 w-8 text-fg-muted" />
			<div className="flex flex-col items-center gap-1">
				<h3 className="text-base font-semibold text-fg-primary">{t("emptyFilteredTitle")}</h3>
				<p className="max-w-md text-sm text-fg-muted">{t("emptyFilteredDescription")}</p>
			</div>
			<Button onClick={clearFilters} type="button" variant="outline">
				{t("emptyFilteredCta")}
			</Button>
		</div>
	);
}
