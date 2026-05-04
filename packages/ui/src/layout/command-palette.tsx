"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Dialog, DialogContent } from "../primitives/dialog";
import { type Scorable, rankItems } from "./fuzzy-match";
import { cn } from "./utils";

export type CommandItemKind = "nav" | "instance" | "rule";

export interface CommandItem extends Scorable {
	readonly id: string;
	readonly kind: CommandItemKind;
	readonly label: string;
	/** Optional secondary text displayed beneath label. */
	readonly hint?: string;
	/** Route href to navigate to on selection. */
	readonly href: string;
	/** Concatenated lowercase haystack used by fuzzy scorer. */
	readonly searchText: string;
}

export interface CommandPaletteStrings {
	readonly title: string;
	readonly placeholder: string;
	readonly emptyTitle: string;
	readonly emptyHint: string;
	readonly loading: string;
	readonly groupNav: string;
	readonly groupInstance: string;
	readonly groupRule: string;
	readonly hintNavigate: string;
	readonly hintSelect: string;
	readonly hintClose: string;
}

export interface CommandPaletteProps {
	readonly open: boolean;
	readonly onOpenChange: (next: boolean) => void;
	readonly items: readonly CommandItem[];
	readonly isLoading: boolean;
	readonly onSelect: (item: CommandItem) => void;
	readonly strings: CommandPaletteStrings;
}

const MAX_RESULTS = 50;

export function CommandPalette(props: CommandPaletteProps) {
	const { open, onOpenChange, items, isLoading, onSelect, strings } = props;
	const [query, setQuery] = useState("");
	const [activeIdx, setActiveIdx] = useState(0);
	const inputRef = useRef<HTMLInputElement | null>(null);
	const listRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		if (!open) {
			setQuery("");
			setActiveIdx(0);
		}
	}, [open]);

	useEffect(() => {
		if (open) {
			const handle = requestAnimationFrame(() => inputRef.current?.focus());
			return () => cancelAnimationFrame(handle);
		}
	}, [open]);

	const ranked = useMemo(() => {
		const results = rankItems(items, query);
		return results.slice(0, MAX_RESULTS).map((entry) => entry.item);
	}, [items, query]);

	useEffect(() => {
		setActiveIdx(0);
	}, []);

	useEffect(() => {
		if (activeIdx >= ranked.length && ranked.length > 0) {
			setActiveIdx(0);
		}
	}, [activeIdx, ranked.length]);

	const choose = useCallback(
		(item: CommandItem) => {
			onSelect(item);
			onOpenChange(false);
		},
		[onSelect, onOpenChange],
	);

	const handleKeyDown = useCallback(
		(event: React.KeyboardEvent<HTMLDivElement>) => {
			if (event.key === "ArrowDown") {
				event.preventDefault();
				setActiveIdx((prev) => (ranked.length === 0 ? 0 : (prev + 1) % ranked.length));
				return;
			}
			if (event.key === "ArrowUp") {
				event.preventDefault();
				setActiveIdx((prev) =>
					ranked.length === 0 ? 0 : (prev - 1 + ranked.length) % ranked.length,
				);
				return;
			}
			if (event.key === "Enter") {
				event.preventDefault();
				const candidate = ranked[activeIdx];
				if (candidate) {
					choose(candidate);
				}
				return;
			}
		},
		[ranked, activeIdx, choose],
	);

	useEffect(() => {
		if (!listRef.current) {
			return;
		}
		const activeEl = listRef.current.querySelector<HTMLElement>(
			`[data-command-idx="${activeIdx}"]`,
		);
		activeEl?.scrollIntoView({ block: "nearest" });
	}, [activeIdx]);

	const grouped = useMemo(() => groupByKind(ranked), [ranked]);

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent onKeyDown={handleKeyDown} className="max-w-2xl p-0" aria-label={strings.title}>
				<div className="border-b border-border-hairline px-4 py-3">
					<input
						ref={inputRef}
						type="text"
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						placeholder={strings.placeholder}
						className={cn(
							"h-10 w-full bg-transparent text-base text-fg-primary placeholder:text-fg-muted",
							"outline-none",
						)}
						aria-label={strings.placeholder}
						aria-autocomplete="list"
						aria-controls="command-palette-list"
					/>
				</div>
				<div
					id="command-palette-list"
					ref={listRef}
					tabIndex={-1}
					// biome-ignore lint/a11y/useSemanticElements: <select> cannot render rich rows; we manage keyboard + roving focus in-line.
					role="listbox"
					aria-label={strings.title}
					className="max-h-[52vh] overflow-y-auto py-2"
				>
					{isLoading ? (
						<div className="px-4 py-6 text-sm text-fg-muted">{strings.loading}</div>
					) : ranked.length === 0 ? (
						<EmptyState title={strings.emptyTitle} hint={strings.emptyHint} />
					) : (
						<GroupedList
							grouped={grouped}
							ranked={ranked}
							activeIdx={activeIdx}
							strings={strings}
							onSelect={choose}
							onHover={setActiveIdx}
						/>
					)}
				</div>
				<Footer strings={strings} />
			</DialogContent>
		</Dialog>
	);
}

function EmptyState(props: { readonly title: string; readonly hint: string }) {
	return (
		<div className="flex flex-col items-center justify-center gap-1 px-4 py-10 text-center">
			<p className="text-sm font-medium text-fg-primary">{props.title}</p>
			<p className="text-xs text-fg-muted">{props.hint}</p>
		</div>
	);
}

interface GroupedListProps {
	readonly grouped: readonly CommandGroup[];
	readonly ranked: readonly CommandItem[];
	readonly activeIdx: number;
	readonly strings: CommandPaletteStrings;
	readonly onSelect: (item: CommandItem) => void;
	readonly onHover: (idx: number) => void;
}

function GroupedList(props: GroupedListProps) {
	const { grouped, ranked, activeIdx, strings, onSelect, onHover } = props;
	return (
		<div>
			{grouped.map((group) => (
				<div key={group.kind} className="mb-2 last:mb-0">
					<div className="px-4 py-1 text-[11px] font-semibold uppercase tracking-wider text-fg-muted">
						{groupLabel(group.kind, strings)}
					</div>
					<ul>
						{group.items.map((item) => {
							const idx = ranked.indexOf(item);
							const active = idx === activeIdx;
							return (
								<li key={item.id}>
									<button
										type="button"
										data-command-idx={idx}
										// biome-ignore lint/a11y/useSemanticElements: role=option on <button> is required for the combobox+listbox pattern; <option> cannot host rich content.
										role="option"
										aria-selected={active}
										onMouseEnter={() => onHover(idx)}
										onClick={() => onSelect(item)}
										className={cn(
											"flex w-full items-center justify-between gap-3 px-4 py-2 text-left text-sm transition-colors",
											active
												? "bg-surface-overlay text-fg-primary"
												: "text-fg-secondary hover:bg-surface-overlay",
										)}
									>
										<div className="flex min-w-0 flex-col">
											<span className="truncate">{item.label}</span>
											{item.hint ? (
												<span className="truncate text-xs text-fg-muted">{item.hint}</span>
											) : null}
										</div>
										<span className="flex-shrink-0 font-mono text-[10px] text-fg-muted">
											{item.href}
										</span>
									</button>
								</li>
							);
						})}
					</ul>
				</div>
			))}
		</div>
	);
}

function Footer(props: { readonly strings: CommandPaletteStrings }) {
	const { strings } = props;
	return (
		<div className="flex items-center gap-4 border-t border-border-hairline px-4 py-2 text-[11px] text-fg-muted">
			<Hint keys={["↑", "↓"]} label={strings.hintNavigate} />
			<Hint keys={["Enter"]} label={strings.hintSelect} />
			<Hint keys={["Esc"]} label={strings.hintClose} />
		</div>
	);
}

function Hint(props: { readonly keys: readonly string[]; readonly label: string }) {
	return (
		<span className="flex items-center gap-1">
			{props.keys.map((k) => (
				<kbd
					key={k}
					className="rounded border border-border-subtle bg-bg-base px-1.5 py-0.5 font-mono text-[10px] text-fg-secondary"
				>
					{k}
				</kbd>
			))}
			<span>{props.label}</span>
		</span>
	);
}

interface CommandGroup {
	readonly kind: CommandItemKind;
	readonly items: readonly CommandItem[];
}

function groupByKind(items: readonly CommandItem[]): readonly CommandGroup[] {
	const order: CommandItemKind[] = ["nav", "instance", "rule"];
	const map = new Map<CommandItemKind, CommandItem[]>();
	for (const item of items) {
		const bucket = map.get(item.kind) ?? [];
		bucket.push(item);
		map.set(item.kind, bucket);
	}
	const result: CommandGroup[] = [];
	for (const kind of order) {
		const bucket = map.get(kind);
		if (bucket && bucket.length > 0) {
			result.push({ kind, items: bucket });
		}
	}
	return result;
}

function groupLabel(kind: CommandItemKind, strings: CommandPaletteStrings): string {
	if (kind === "nav") return strings.groupNav;
	if (kind === "instance") return strings.groupInstance;
	return strings.groupRule;
}

interface EnterCommandPaletteParams {
	readonly wantsToggleOpen: (event: KeyboardEvent) => boolean;
}

/**
 * Register a keyboard shortcut that toggles the palette open/close on the
 * document. Returns an unsubscribe function.
 */
export function registerCommandPaletteShortcut(
	toggle: () => void,
	params: EnterCommandPaletteParams = {
		wantsToggleOpen: (event) =>
			(event.metaKey || event.ctrlKey) && !event.shiftKey && !event.altKey && event.key === "k",
	},
): () => void {
	const listener = (event: KeyboardEvent) => {
		if (params.wantsToggleOpen(event)) {
			event.preventDefault();
			toggle();
		}
	};
	document.addEventListener("keydown", listener);
	return () => document.removeEventListener("keydown", listener);
}
