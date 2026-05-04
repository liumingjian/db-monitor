import { useTranslations } from "next-intl";

import { ParticlesBackground } from "./particles-background";

interface ValueItem {
	readonly key: "monitoring" | "alert" | "audit";
	readonly titleKey: "valueMonitoring" | "valueAlert" | "valueAudit";
	readonly descKey: "valueMonitoringDesc" | "valueAlertDesc" | "valueAuditDesc";
}

const VALUE_ITEMS: readonly ValueItem[] = [
	{ key: "monitoring", titleKey: "valueMonitoring", descKey: "valueMonitoringDesc" },
	{ key: "alert", titleKey: "valueAlert", descKey: "valueAlertDesc" },
	{ key: "audit", titleKey: "valueAudit", descKey: "valueAuditDesc" },
];

export function BrandPanel() {
	const t = useTranslations("loginPage");
	const tCommon = useTranslations("common");
	return (
		<section className="relative isolate flex h-full w-full flex-col justify-between overflow-hidden bg-bg-deep px-10 py-12 md:px-14 md:py-16">
			<ParticlesBackground />
			<header className="relative z-10 flex items-center gap-3">
				<span
					aria-hidden="true"
					className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-accent text-on-accent font-bold"
				>
					D
				</span>
				<span className="text-sm font-semibold tracking-wide text-fg-primary">
					{tCommon("appName")}
				</span>
			</header>
			<div className="relative z-10 flex max-w-xl flex-col gap-6">
				<p className="text-xs font-semibold uppercase tracking-[0.32em] text-accent">
					{t("heroEyebrow")}
				</p>
				<h1 className="text-4xl font-semibold leading-tight text-fg-primary md:text-5xl">
					{t("heroTitle")}
				</h1>
				<p className="text-base leading-7 text-fg-secondary md:text-lg">{t("heroTagline")}</p>
			</div>
			<ul className="relative z-10 grid gap-4 md:grid-cols-3">
				{VALUE_ITEMS.map((item) => (
					<li
						key={item.key}
						className="rounded-md border border-border-hairline bg-bg-elevated/70 p-4 backdrop-blur-sm"
					>
						<p className="text-sm font-semibold text-fg-primary">{t(item.titleKey)}</p>
						<p className="mt-1 text-xs leading-5 text-fg-muted">{t(item.descKey)}</p>
					</li>
				))}
			</ul>
		</section>
	);
}
