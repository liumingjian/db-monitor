"use client";

import { Button, useToast } from "@db-monitor/ui";
import { RefreshCw as RefreshIcon } from "lucide-react";
import { useTranslations } from "next-intl";
import { useCallback, useTransition } from "react";

import { validateInstanceAction } from "../../monitoring-actions";

interface RevalidateInstanceButtonProps {
	readonly instanceId: string;
	readonly instanceName: string;
	readonly variant?: "default" | "outline" | "ghost";
	readonly size?: "sm" | "md";
}

/**
 * 行级 / 卡级"重验证"按钮：
 * - 点击 → 调用 `validateInstanceAction` server action（真实 POST）
 * - pending 期间禁用，防连点
 * - 成功 / 失败分别 Toast（Q16 规则 3）
 */
export function RevalidateInstanceButton(props: RevalidateInstanceButtonProps) {
	const { instanceId, instanceName, variant = "outline", size = "sm" } = props;
	const t = useTranslations("instancesPage");
	const { toast } = useToast();
	const [pending, startTransition] = useTransition();

	const handleClick = useCallback(() => {
		startTransition(async () => {
			const form = new FormData();
			form.set("instance_id", instanceId);
			try {
				await validateInstanceAction(form);
				toast({
					title: t("revalidateSuccessTitle"),
					description: t("revalidateSuccessDescription", { name: instanceName }),
					variant: "success",
				});
			} catch (error) {
				toast({
					title: t("revalidateFailureTitle"),
					description: error instanceof Error ? error.message : String(error),
					variant: "error",
				});
			}
		});
	}, [instanceId, instanceName, t, toast]);

	return (
		<Button disabled={pending} onClick={handleClick} size={size} variant={variant}>
			<RefreshIcon aria-hidden="true" className="h-4 w-4" />
			<span>{pending ? t("revalidatePending") : t("revalidateLabel")}</span>
		</Button>
	);
}
