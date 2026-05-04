/**
 * Local, zero-dependency fuzzy scorer for the ⌘K command palette.
 *
 * Design goals (Q17 rule #2):
 *   - Pure TS, no runtime deps (no fuse.js / no levenshtein).
 *   - Token-aware: a query matches if every whitespace-separated token fuzz-matches.
 *   - Bonuses reflect user expectation:
 *       * exact match        → 1000
 *       * prefix of haystack → +400
 *       * whole token match  → +200
 *       * contiguous run     → +N per consecutive char
 *       * start-of-word      → +12 per such char
 *   - Case-insensitive but keeps original for highlight ranges.
 */

const PREFIX_BONUS = 400;
const WORD_START_BONUS = 12;
const CONTIGUOUS_BONUS = 6;
const MATCH_BASE = 1;
const TOKEN_FULL_MATCH_BONUS = 200;
const EXACT_MATCH_SCORE = 1000;
const DISTANCE_PENALTY_PER_GAP = 1;

export interface FuzzyMatch {
	readonly score: number;
	/** Sorted ascending indexes of matched characters in the original haystack. */
	readonly indexes: readonly number[];
}

/**
 * Match a single lowercase token against a haystack.
 * Returns `null` if no subsequence match exists.
 */
function matchSingleToken(
	haystackLower: string,
	haystack: string,
	tokenLower: string,
): FuzzyMatch | null {
	if (tokenLower.length === 0) {
		return { score: 0, indexes: [] };
	}
	if (haystackLower === tokenLower) {
		return {
			score: EXACT_MATCH_SCORE,
			indexes: Array.from({ length: haystack.length }, (_, i) => i),
		};
	}
	if (haystackLower.startsWith(tokenLower)) {
		const indexes = Array.from({ length: tokenLower.length }, (_, i) => i);
		return { score: PREFIX_BONUS + scoreIndexes(haystack, indexes), indexes };
	}

	let tokenIdx = 0;
	let lastMatched = -2;
	const indexes: number[] = [];
	for (let i = 0; i < haystackLower.length && tokenIdx < tokenLower.length; i += 1) {
		if (haystackLower[i] === tokenLower[tokenIdx]) {
			indexes.push(i);
			lastMatched = i;
			tokenIdx += 1;
		}
	}
	if (tokenIdx < tokenLower.length) {
		return null;
	}
	void lastMatched;

	// Full substring (non-prefix) bonus
	const substringIdx = haystackLower.indexOf(tokenLower);
	if (substringIdx >= 0) {
		const contiguous = Array.from({ length: tokenLower.length }, (_, i) => substringIdx + i);
		return {
			score: TOKEN_FULL_MATCH_BONUS + scoreIndexes(haystack, contiguous),
			indexes: contiguous,
		};
	}

	return { score: scoreIndexes(haystack, indexes), indexes };
}

function scoreIndexes(haystack: string, indexes: readonly number[]): number {
	if (indexes.length === 0) {
		return 0;
	}
	let score = indexes.length * MATCH_BASE;
	for (let k = 0; k < indexes.length; k += 1) {
		const idx = indexes[k] as number;
		if (idx === 0 || isWordBoundary(haystack, idx)) {
			score += WORD_START_BONUS;
		}
		if (k > 0) {
			const prev = indexes[k - 1] as number;
			if (idx === prev + 1) {
				score += CONTIGUOUS_BONUS;
			} else {
				score -= (idx - prev - 1) * DISTANCE_PENALTY_PER_GAP;
			}
		}
	}
	return score;
}

function isWordBoundary(haystack: string, idx: number): boolean {
	if (idx <= 0) {
		return true;
	}
	const prev = haystack.charAt(idx - 1);
	return !/[A-Za-z0-9一-鿿]/.test(prev);
}

/**
 * Score a haystack against a multi-token query.
 * All tokens must match; returns `null` otherwise.
 */
export function fuzzyScore(haystack: string, query: string): FuzzyMatch | null {
	const q = query.trim();
	if (q.length === 0) {
		return { score: 0, indexes: [] };
	}
	const haystackLower = haystack.toLowerCase();
	const tokens = q.toLowerCase().split(/\s+/u).filter(Boolean);
	if (tokens.length === 0) {
		return { score: 0, indexes: [] };
	}

	let total = 0;
	const merged = new Set<number>();
	for (const token of tokens) {
		const m = matchSingleToken(haystackLower, haystack, token);
		if (m === null) {
			return null;
		}
		total += m.score;
		for (const idx of m.indexes) {
			merged.add(idx);
		}
	}
	return {
		score: total,
		indexes: Array.from(merged).sort((a, b) => a - b),
	};
}

export interface Scorable {
	readonly searchText: string;
}

export interface ScoredItem<T extends Scorable> {
	readonly item: T;
	readonly match: FuzzyMatch;
}

/**
 * Rank a list of items by fuzzy match score, descending.
 * Items without a match are dropped.
 */
export function rankItems<T extends Scorable>(
	items: readonly T[],
	query: string,
): readonly ScoredItem<T>[] {
	const trimmed = query.trim();
	if (trimmed.length === 0) {
		return items.map((item) => ({ item, match: { score: 0, indexes: [] } }));
	}
	const scored: ScoredItem<T>[] = [];
	for (const item of items) {
		const match = fuzzyScore(item.searchText, trimmed);
		if (match !== null) {
			scored.push({ item, match });
		}
	}
	scored.sort((a, b) => b.match.score - a.match.score);
	return scored;
}
