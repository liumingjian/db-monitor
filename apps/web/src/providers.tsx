"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useState } from "react";

import { createShellQueryClient } from "./data-layer";

interface ShellProvidersProps {
	readonly children: ReactNode;
}

export function ShellProviders({ children }: ShellProvidersProps) {
	const [queryClient] = useState(() => createShellQueryClient());
	return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
