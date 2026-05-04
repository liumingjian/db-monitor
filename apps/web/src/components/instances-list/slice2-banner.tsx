"use client";

import { X as XIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

const LOCAL_STORAGE_KEY = "instances.slice2Banner.dismissed";

/**
 * 底部浅色横幅："批量运维能力将在 Slice 2 交付"。
 *
 * - `×` 关闭 → localStorage 写 `instances.slice2Banner.dismissed=1`
 * - hydration-safe：初始态 = 显示（SSR 永远渲染）；mount 后 useEffect 若已关闭则隐藏
 *   （最多一帧闪烁，但永远不会出现 "服务端显示 / 客户端隐藏" 的错配警告）
 */
export function Slice2Banner() {
	const t = useTranslations("instancesPage");
	const [dismissed, setDismissed] = useState(false);

	useEffect(() => {
		try {
			if (window.localStorage.getItem(LOCAL_STORAGE_KEY) === "1") {
				setDismissed(true);
			}
		} catch {
			// localStorage 被禁用（隐私模式 / 企业策略） → 当作未关闭即可。
		}
	}, []);

	if (dismissed) {
		return null;
	}

	const handleDismiss = () => {
		setDismissed(true);
		try {
			window.localStorage.setItem(LOCAL_STORAGE_KEY, "1");
		} catch {
			// 忽略；下次进入仍会展示，属可接受降级。
		}
	};

	return (
		<div className="flex items-start justify-between gap-3 rounded-md border border-border-hairline bg-accent/5 px-4 py-3 text-sm text-fg-secondary">
			<div className="flex flex-col gap-0.5">
				<p className="font-medium text-fg-primary">{t("slice2BannerTitle")}</p>
				<p className="text-xs text-fg-muted">{t("slice2BannerDescription")}</p>
			</div>
			<button
				aria-label={t("slice2BannerDismiss")}
				className="text-fg-muted hover:text-fg-primary"
				onClick={handleDismiss}
				type="button"
			>
				<XIcon aria-hidden="true" className="h-4 w-4" />
			</button>
		</div>
	);
}
