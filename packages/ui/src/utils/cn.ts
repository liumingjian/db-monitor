import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Merge Tailwind class names with dedup, preserving later-wins semantics.
 */
export function cn(...inputs: ClassValue[]): string {
	return twMerge(clsx(inputs));
}
