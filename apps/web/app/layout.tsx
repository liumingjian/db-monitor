import type { Metadata } from "next";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getMessages, getTranslations } from "next-intl/server";
import type { ReactNode } from "react";

import { ShellProviders } from "../src/providers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
	const t = await getTranslations("common");
	return {
		title: t("appName"),
		description: t("appTaglineLong"),
	};
}

interface RootLayoutProps {
	readonly children: ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {
	const locale = await getLocale();
	const messages = await getMessages();

	return (
		<html lang={locale} data-theme="dark" suppressHydrationWarning>
			<body>
				<NextIntlClientProvider locale={locale} messages={messages}>
					<ShellProviders>{children}</ShellProviders>
				</NextIntlClientProvider>
			</body>
		</html>
	);
}
