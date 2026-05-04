"use client";

import { Button, Tooltip } from "@db-monitor/ui";
import { Pencil as PencilIcon, Trash2 as TrashIcon } from "lucide-react";
import { useTranslations } from "next-intl";

interface RowPlaceholdersProps {
	readonly compact?: boolean;
}

/**
 * 行/卡级 Tier 3 按钮占位：编辑、删除。
 *
 * 渲染 `disabled` 按钮 + Tooltip "将在 Slice 2 上线"；**禁止**绑定任何 server action。
 */
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

/**
 * 顶部批量操作占位：批量启用 / 批量停用 / 批量删除。
 *
 * 整组 `disabled` + Tooltip 标 Slice 2；不提供 checkbox / 选中态。
 */
export function BulkTier3Placeholders() {
	const t = useTranslations("instancesPage");
	return (
		<div className="flex flex-wrap items-center gap-2 rounded-md border border-dashed border-border-subtle bg-bg-base/60 px-3 py-2">
			<span className="text-xs font-medium uppercase tracking-widest text-fg-muted">
				{t("tier3BulkSectionLabel")}
			</span>
			<Tooltip content={t("tier3BulkEnableTooltip")} side="top">
				<Button disabled size="sm" variant="ghost">
					{t("tier3BulkEnableLabel")}
				</Button>
			</Tooltip>
			<Tooltip content={t("tier3BulkDisableTooltip")} side="top">
				<Button disabled size="sm" variant="ghost">
					{t("tier3BulkDisableLabel")}
				</Button>
			</Tooltip>
			<Tooltip content={t("tier3BulkDeleteTooltip")} side="top">
				<Button disabled size="sm" variant="ghost">
					{t("tier3BulkDeleteLabel")}
				</Button>
			</Tooltip>
		</div>
	);
}
