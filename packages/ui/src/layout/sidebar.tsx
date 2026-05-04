"use client";

import { PanelLeft, PanelLeftClose } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { type ReactNode, useEffect, useState } from "react";
import { useSidebarMobile } from "./sidebar-mobile";
import type { SidebarGroup, SidebarItemModel } from "./types";
import { cn } from "./utils";

const STORAGE_KEY = "ui.sidebar.collapsed";
const SECTION_ORDER: readonly SidebarGroup[] = ["observe", "alert", "operate", "admin"];

export interface SidebarStrings {
	readonly toggleCollapse: string;
	readonly toggleExpand: string;
	readonly navigationLabel: string;
	readonly sectionLabels: Readonly<Record<SidebarGroup, string>>;
}

export interface SidebarProps {
	readonly items: readonly SidebarItemModel[];
	readonly footer?: ReactNode;
	readonly strings: SidebarStrings;
}

export function Sidebar(props: SidebarProps) {
	const { items, footer, strings } = props;
	const collapsed = useCollapsedState();
	const pathname = usePathname() ?? "";
	const mobile = useSidebarMobile();

	// Close the mobile drawer whenever the route changes.
	useEffect(() => {
		void pathname;
		mobile.close();
	}, [pathname, mobile.close]);

	return (
		<>
			<DesktopSidebar
				collapsed={collapsed.value}
				footer={footer}
				items={items}
				onToggleCollapsed={collapsed.toggle}
				pathname={pathname}
				strings={strings}
			/>
			<MobileSidebarDrawer
				footer={footer}
				items={items}
				onClose={mobile.close}
				open={mobile.open}
				pathname={pathname}
				strings={strings}
			/>
		</>
	);
}

interface DesktopSidebarProps {
	readonly collapsed: boolean;
	readonly footer: ReactNode;
	readonly items: readonly SidebarItemModel[];
	readonly onToggleCollapsed: () => void;
	readonly pathname: string;
	readonly strings: SidebarStrings;
}

function DesktopSidebar(props: DesktopSidebarProps) {
	const { collapsed, footer, items, onToggleCollapsed, pathname, strings } = props;
	const ToggleIcon = collapsed ? PanelLeft : PanelLeftClose;
	const toggleLabel = collapsed ? strings.toggleExpand : strings.toggleCollapse;

	return (
		<aside
			aria-expanded={!collapsed}
			aria-label={strings.navigationLabel}
			className={cn(
				"hidden h-full shrink-0 flex-col border-r border-border-hairline bg-bg-base md:flex",
				"transition-[width] duration-200 ease-out",
				collapsed ? "w-16" : "w-60",
			)}
		>
			<div
				className={cn(
					"flex h-12 shrink-0 items-center border-b border-border-hairline",
					collapsed ? "justify-center" : "justify-end px-2",
				)}
			>
				<button
					aria-label={toggleLabel}
					className="flex h-8 w-8 items-center justify-center rounded-md text-fg-muted hover:bg-surface-overlay hover:text-fg-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
					onClick={onToggleCollapsed}
					title={toggleLabel}
					type="button"
				>
					<ToggleIcon aria-hidden="true" className="h-4 w-4" />
				</button>
			</div>
			<nav className="flex-1 overflow-y-auto py-2">
				{SECTION_ORDER.map((group) => (
					<SidebarSection
						collapsed={collapsed}
						group={group}
						items={items}
						key={group}
						label={strings.sectionLabels[group]}
						pathname={pathname}
					/>
				))}
			</nav>
			{footer ? (
				<div
					className={cn(
						"border-t border-border-hairline py-2",
						collapsed ? "flex flex-col items-center gap-1" : "px-2",
					)}
				>
					{footer}
				</div>
			) : null}
		</aside>
	);
}

interface MobileSidebarDrawerProps {
	readonly footer: ReactNode;
	readonly items: readonly SidebarItemModel[];
	readonly onClose: () => void;
	readonly open: boolean;
	readonly pathname: string;
	readonly strings: SidebarStrings;
}

function MobileSidebarDrawer(props: MobileSidebarDrawerProps) {
	const { footer, items, onClose, open, pathname, strings } = props;
	return (
		<div
			aria-hidden={!open}
			className={cn(
				"fixed inset-0 z-50 md:hidden",
				open ? "pointer-events-auto" : "pointer-events-none",
			)}
		>
			<button
				aria-label={strings.toggleCollapse}
				className={cn(
					"absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity duration-200",
					open ? "opacity-100" : "opacity-0",
				)}
				onClick={onClose}
				tabIndex={open ? 0 : -1}
				type="button"
			/>
			<aside
				aria-expanded={open}
				aria-label={strings.navigationLabel}
				className={cn(
					"absolute inset-y-0 left-0 flex w-64 flex-col border-r border-border-hairline bg-bg-base shadow-2xl",
					"transition-transform duration-200 ease-out",
					open ? "translate-x-0" : "-translate-x-full",
				)}
			>
				<div className="flex h-12 shrink-0 items-center border-b border-border-hairline px-2" />
				<nav className="flex-1 overflow-y-auto py-2">
					{SECTION_ORDER.map((group) => (
						<SidebarSection
							collapsed={false}
							group={group}
							items={items}
							key={group}
							label={strings.sectionLabels[group]}
							pathname={pathname}
						/>
					))}
				</nav>
				{footer ? <div className="border-t border-border-hairline px-2 py-2">{footer}</div> : null}
			</aside>
		</div>
	);
}

interface SidebarSectionProps {
	readonly group: SidebarGroup;
	readonly items: readonly SidebarItemModel[];
	readonly collapsed: boolean;
	readonly label: string;
	readonly pathname: string;
}

function SidebarSection(props: SidebarSectionProps) {
	const { group, items, collapsed, label, pathname } = props;
	const groupItems = items.filter((item) => item.group === group);
	if (groupItems.length === 0) {
		return null;
	}
	return (
		<div className="border-b border-border-hairline py-2 last:border-b-0">
			{collapsed ? null : (
				<h2 className="mb-1 px-3 text-[11px] font-medium uppercase tracking-widest text-fg-muted">
					{label}
				</h2>
			)}
			<ul className="flex flex-col gap-0.5 px-2">
				{groupItems.map((item) => (
					<li key={item.href}>
						<SidebarRow
							active={isItemActive(pathname, item.href)}
							collapsed={collapsed}
							item={item}
						/>
					</li>
				))}
			</ul>
		</div>
	);
}

interface SidebarRowProps {
	readonly item: SidebarItemModel;
	readonly collapsed: boolean;
	readonly active: boolean;
}

function SidebarRow(props: SidebarRowProps) {
	const { item, collapsed, active } = props;
	const Icon = item.icon;
	return (
		<Link
			aria-current={active ? "page" : undefined}
			className={cn(
				"relative flex h-9 items-center gap-3 rounded-md text-sm",
				"transition-colors duration-150 ease-out",
				"focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
				collapsed ? "justify-center" : "px-2",
				active
					? "bg-accent/10 text-accent"
					: "text-fg-secondary hover:bg-surface-overlay hover:text-fg-primary",
			)}
			href={item.href}
			title={collapsed ? item.label : undefined}
		>
			{active ? (
				<span
					aria-hidden="true"
					className="absolute left-0 top-1/2 h-6 w-[2px] -translate-y-1/2 rounded-r bg-accent"
				/>
			) : null}
			{Icon ? <Icon aria-hidden="true" className="h-4 w-4 shrink-0" /> : null}
			{collapsed ? null : (
				<>
					<span className="flex-1 truncate">{item.label}</span>
					{item.badge !== undefined ? (
						<span
							className={cn(
								"inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[11px] font-medium",
								active ? "bg-accent text-on-accent" : "bg-surface-overlay text-fg-muted",
							)}
						>
							{item.badge}
						</span>
					) : null}
				</>
			)}
		</Link>
	);
}

interface CollapsedState {
	readonly value: boolean;
	readonly toggle: () => void;
}

function useCollapsedState(): CollapsedState {
	const [collapsed, setCollapsed] = useState(false);

	useEffect(() => {
		const stored = window.localStorage.getItem(STORAGE_KEY);
		if (stored === "true") {
			setCollapsed(true);
		}
	}, []);

	useEffect(() => {
		window.localStorage.setItem(STORAGE_KEY, collapsed ? "true" : "false");
	}, [collapsed]);

	useEffect(() => {
		function onKey(event: KeyboardEvent) {
			if (event.key !== "[" || event.metaKey || event.ctrlKey || event.altKey) {
				return;
			}
			const target = event.target;
			if (target instanceof HTMLElement) {
				const tag = target.tagName;
				if (tag === "INPUT" || tag === "TEXTAREA" || target.isContentEditable) {
					return;
				}
			}
			event.preventDefault();
			setCollapsed((current) => !current);
		}
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, []);

	const toggle = () => setCollapsed((current) => !current);

	return { value: collapsed, toggle };
}

function isItemActive(pathname: string, href: string): boolean {
	if (pathname === href) {
		return true;
	}
	return pathname.startsWith(`${href}/`);
}
