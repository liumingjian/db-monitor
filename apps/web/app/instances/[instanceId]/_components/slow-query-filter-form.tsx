import type { SlowQueryFilterValues } from "../../../../src/slow-queries-ui";

interface SlowQueryFilterFormProps {
	readonly action: string;
	readonly filters: SlowQueryFilterValues;
}

export function SlowQueryFilterForm({ action, filters }: SlowQueryFilterFormProps) {
	return (
		<form
			action={action}
			className="grid gap-3 rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4 md:grid-cols-3"
			method="get"
		>
			<TextInput
				defaultValue={filters.minDurationMs}
				inputMode="numeric"
				label="Min duration (ms)"
				name="minDurationMs"
				placeholder="1000"
			/>
			<TextInput
				defaultValue={filters.user}
				label="User"
				name="user"
				placeholder="e.g. app"
			/>
			<TextInput
				defaultValue={filters.schema}
				label="Schema"
				name="schema"
				placeholder="e.g. ordering"
			/>
			<TextInput
				defaultValue={filters.digestPrefix}
				label="Digest prefix"
				name="digestPrefix"
				placeholder="abc"
			/>
			<TextInput
				defaultValue={filters.startedAfter}
				label="Started after"
				name="startedAfter"
				placeholder="ISO 8601"
			/>
			<TextInput
				defaultValue={filters.startedBefore}
				label="Started before"
				name="startedBefore"
				placeholder="ISO 8601"
			/>
			<div className="flex items-end gap-2 md:col-span-3">
				<button
					className="rounded-[0.9rem] bg-[var(--accent)] px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:opacity-90"
					type="submit"
				>
					Apply filters
				</button>
				<a
					className="rounded-[0.9rem] border border-black/10 bg-white px-5 py-2.5 text-sm font-semibold text-[var(--muted)] hover:border-[var(--accent)] hover:text-[var(--ink)]"
					href={action}
				>
					Reset
				</a>
			</div>
		</form>
	);
}

interface TextInputProps {
	readonly defaultValue: string;
	readonly inputMode?: "numeric" | "text";
	readonly label: string;
	readonly name: string;
	readonly placeholder?: string;
}

function TextInput({ defaultValue, inputMode, label, name, placeholder }: TextInputProps) {
	return (
		<label className="grid gap-1 text-sm" htmlFor={`slow-query-${name}`}>
			<span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
				{label}
			</span>
			<input
				className="rounded-[0.9rem] border border-black/10 bg-white px-3 py-2 text-sm text-[var(--ink)]"
				defaultValue={defaultValue}
				id={`slow-query-${name}`}
				inputMode={inputMode}
				name={name}
				placeholder={placeholder}
				type="text"
			/>
		</label>
	);
}
