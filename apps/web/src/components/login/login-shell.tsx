"use client";

import { ThemeToggle } from "@db-monitor/ui";
import { useTranslations } from "next-intl";

import { BrandPanel } from "./brand-panel";
import { LoginForm } from "./login-form";

interface LoginShellProps {
	readonly nextPath: string;
}

export function LoginShell({ nextPath }: LoginShellProps) {
	const t = useTranslations("loginPage");
	return (
		<main className="relative grid min-h-screen w-full grid-cols-1 bg-bg-deep md:grid-cols-[6fr_4fr]">
			<div className="relative min-h-[40vh] md:min-h-screen">
				<BrandPanel />
			</div>
			<section className="relative flex min-h-[60vh] items-center justify-center bg-bg-base px-6 py-10 md:min-h-screen">
				<div className="absolute right-4 top-4 z-10">
					<ThemeToggle
						className="border border-border-hairline bg-surface-overlay text-fg-primary hover:bg-bg-elevated focus-visible:ring-offset-2 focus-visible:ring-offset-bg-base"
						labelDark={t("themeToggleDark")}
						labelLight={t("themeToggleLight")}
					/>
				</div>
				<LoginForm nextPath={nextPath} />
			</section>
		</main>
	);
}
