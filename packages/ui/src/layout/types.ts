import type { ComponentType, ReactNode, SVGProps } from "react";

/**
 * A lucide-style icon component. Accepts standard SVG props plus `size`.
 */
export type IconComponent = ComponentType<SVGProps<SVGSVGElement>>;

/**
 * The four top-level groups surfaced on the left 64px icon rail.
 */
export type IconRailGroupId = "observe" | "alert" | "operate" | "admin";

export interface IconRailGroup {
	readonly id: IconRailGroupId;
	readonly label: string;
	readonly icon: IconComponent;
	readonly href: string;
	/** Route prefixes that mark this group active (longest-prefix wins). */
	readonly matchPrefixes: readonly string[];
}

export interface SidebarItemModel {
	readonly href: string;
	readonly label: string;
	readonly icon?: IconComponent;
	readonly badge?: string | number;
	readonly children?: readonly SidebarItemModel[];
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
