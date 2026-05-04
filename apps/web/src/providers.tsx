"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useState } from "react";

import {
	AppCommandPalette,
	AppNotificationDrawer,
	CommandPaletteProvider,
	NotificationCenterProvider,
	OnCallProvider,
} from "./components/shell";
import { createShellQueryClient } from "./data-layer";

interface ShellProvidersProps {
	readonly children: ReactNode;
}

export function ShellProviders({ children }: ShellProvidersProps) {
	const [queryClient] = useState(() => createShellQueryClient());
	return (
		<QueryClientProvider client={queryClient}>
			<OnCallProvider>
				<CommandPaletteProvider>
					<NotificationCenterProvider>
						{children}
						<AppCommandPalette />
						<AppNotificationDrawer />
					</NotificationCenterProvider>
				</CommandPaletteProvider>
			</OnCallProvider>
		</QueryClientProvider>
	);
}
