import type { ComponentType, ReactNode, SVGProps } from "react";

/**
 * A lucide-style icon component. Accepts standard SVG props plus `size`.
 */
export type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

/**
 * The four top-level navigation groups (ADR-0012 D6 Tier 分层 / ADR-0016 D4').
 */
export type SidebarGroup = "observe" | "alert" | "operate" | "admin";

export interface SidebarItemModel {
	readonly group: SidebarGroup;
	readonly href: string;
	readonly label: string;
	readonly icon?: IconComponent;
	readonly badge?: string | number;
}

export interface BreadcrumbItem {
	readonly label: string;
	readonly href?: string;
}

export type SeverityTone = "critical" | "warning" | "info" | "ok";

export interface EntityBadgeModel {
	readonly tone: SeverityTone;
	readonly label: string;
}

export interface QuickMetricItem {
	readonly key: string;
	readonly label: string;
	readonly value: string;
	readonly hint?: string;
	readonly sparkline?: ReactNode;
}

export interface TabItem {
	readonly key: string;
	readonly label: string;
	readonly href?: string;
	readonly badge?: string | number;
	readonly disabled?: boolean;
}
