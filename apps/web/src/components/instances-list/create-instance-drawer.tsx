"use client";

import {
	Dialog,
	DialogBody,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
	Input,
	Label,
	Select,
} from "@db-monitor/ui";
import { INSTANCE_FORM_FIELDS } from "@db-monitor/ui";
import { useTranslations } from "next-intl";

import { createInstanceAction } from "../../monitoring-actions";

interface CreateInstanceDrawerProps {
	readonly open: boolean;
	readonly onOpenChange: (next: boolean) => void;
}

/**
 * 新建实例抽屉（使用 Dialog primitive 的 modal 形态）。
 *
 * - 表单 action = `createInstanceAction`（已存在；成功后 redirect 到新实例详情页）。
 * - 字段复用 `INSTANCE_FORM_FIELDS` + 引擎切换（mysql / oracle）。
 * - 不做前端校验旁路：必填由后端负责；本地仅设置 `required` 以获取浏览器默认 UX。
 */
export function CreateInstanceDrawer(props: CreateInstanceDrawerProps) {
	const { open, onOpenChange } = props;
	const t = useTranslations("instancesPage");

	return (
		<Dialog onOpenChange={onOpenChange} open={open}>
			<DialogContent className="max-w-2xl">
				<DialogHeader>
					<DialogTitle>{t("createTitle")}</DialogTitle>
					<DialogDescription>{t("createDescription")}</DialogDescription>
				</DialogHeader>
				<form action={createInstanceAction}>
					<DialogBody>
						<div className="grid gap-3 md:grid-cols-2">
							<div className="flex flex-col gap-1.5 md:col-span-2">
								<Label htmlFor="create-instance-engine" required>
									{t("createFieldEngine")}
								</Label>
								<Select defaultValue="mysql" id="create-instance-engine" name="engine" required>
									<option value="mysql">{t("engineOptionMysql")}</option>
									<option value="oracle">{t("engineOptionOracle")}</option>
								</Select>
							</div>
							{INSTANCE_FORM_FIELDS.map((field) => (
								<div className="flex flex-col gap-1.5" key={field.name}>
									<Label htmlFor={`create-instance-${field.name}`} required>
										{t(`createField_${field.name}`)}
									</Label>
									<Input
										id={`create-instance-${field.name}`}
										name={field.name}
										placeholder={field.placeholder}
										required
										type={field.type}
									/>
								</div>
							))}
						</div>
					</DialogBody>
					<DialogFooter>
						<button
							className="inline-flex h-9 items-center rounded-md border border-border-subtle bg-transparent px-4 text-sm font-medium text-fg-primary hover:bg-surface-overlay"
							onClick={() => onOpenChange(false)}
							type="button"
						>
							{t("createCancel")}
						</button>
						<button
							className="inline-flex h-9 items-center rounded-md bg-accent px-4 text-sm font-semibold text-on-accent hover:bg-accent-hover"
							type="submit"
						>
							{t("createSubmit")}
						</button>
					</DialogFooter>
				</form>
			</DialogContent>
		</Dialog>
	);
}
