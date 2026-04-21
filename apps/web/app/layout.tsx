import type { Metadata } from "next";
import { Bricolage_Grotesque, IBM_Plex_Sans } from "next/font/google";
import type { ReactNode } from "react";

import { ShellProviders } from "../src/providers";
import "./globals.css";

const bodyFont = IBM_Plex_Sans({
	subsets: ["latin"],
	variable: "--font-body",
	weight: ["400", "500", "600"],
});

const displayFont = Bricolage_Grotesque({
	subsets: ["latin"],
	variable: "--font-display",
	weight: ["500", "700"],
});

export const metadata: Metadata = {
	description: "Mixed-engine monitoring shell with honest overview coverage boundaries",
	title: "DB Monitor",
};

interface RootLayoutProps {
	readonly children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
	return (
		<html className={`${bodyFont.variable} ${displayFont.variable}`} lang="en">
			<body>
				<ShellProviders>{children}</ShellProviders>
			</body>
		</html>
	);
}
