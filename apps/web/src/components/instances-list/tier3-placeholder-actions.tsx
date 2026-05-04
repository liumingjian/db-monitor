"use client";

import { Button, Tooltip } from "@db-monitor/ui";
import { Clock as ClockIcon, Pencil as PencilIcon, Trash2 as TrashIcon } from "lucide-react";
import { useTranslations } from "next-intl";

interface RowPlaceholdersProps {
	readonly compact?: boolean;
}

// 行/卡级 Tier 3 按钮占位：编辑、删除。
// 渲染 disabled 按钮 + Tooltip 说明能力即将上线；禁止绑定 server action。
export function RowTier3Placeholders(props: RowPlaceholdersProps) {
	const { compact = false } = props;
	const t = useTranslations("instancesPage");
	return (
		<div className="inline-flex items-center gap-1">
			<Tooltip content={t("tier3EditTooltip")} side="top">
				<Button aria-label={t("tier3EditLabel")} disabled size="sm" variant="ghost">
					<PencilIcon aria-hidden="true" className="h-4 w-4" />
					{compact ? null : <span>{t("tier3EditLabel")}</span>}
				</Button>
			</Tooltip>
			<Tooltip content={t("tier3DeleteTooltip")} side="top">
				<Button aria-label={t("tier3DeleteLabel")} disabled size="sm" variant="ghost">
					<TrashIcon aria-hidden="true" className="h-4 w-4" />
					{compact ? null : <span>{t("tier3DeleteLabel")}</span>}
				</Button>
			</Tooltip>
		</div>
	);
}

// 顶部批量操作占位：从 3 个 disabled 按钮折叠为一行 inline notice，
// 避免 dead UI。完整能力上线后会替换成真实操作组。
export function BulkTier3Placeholders() {
	const t = useTranslations("instancesPage");
	return (
		<div className="inline-flex items-center gap-2 rounded-md border border-dashed border-border-subtle bg-bg-base/60 px-3 py-1.5 text-xs text-fg-muted">
			<ClockIcon aria-hidden="true" className="h-3.5 w-3.5" />
			<span className="font-medium uppercase tracking-widest text-fg-secondary">
				{t("tier3BulkSectionLabel")}
			</span>
			<span aria-hidden="true" className="text-fg-disabled">
				·
			</span>
			<span>{t("tier3BulkSectionNotice")}</span>
		</div>
	);
}
