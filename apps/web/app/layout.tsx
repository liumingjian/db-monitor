import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@fontsource/ibm-plex-sans/latin-400.css";
import "@fontsource/ibm-plex-sans/latin-500.css";
import "@fontsource/ibm-plex-sans/latin-600.css";
import "@fontsource-variable/bricolage-grotesque/wght.css";

import { ShellProviders } from "../src/providers";
import "./globals.css";

export const metadata: Metadata = {
	description: "Mixed-engine monitoring shell with honest overview coverage boundaries",
	title: "DB Monitor",
};

interface RootLayoutProps {
	readonly children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
	return (
		<html lang="en">
			<body>
				<ShellProviders>{children}</ShellProviders>
			</body>
		</html>
	);
}
