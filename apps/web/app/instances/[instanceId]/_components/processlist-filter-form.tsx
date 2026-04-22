import type { ProcesslistFilterValues } from "../../../../src/processlist-ui";

interface ProcesslistFilterFormProps {
	readonly action: string;
	readonly filters: ProcesslistFilterValues;
}

export function ProcesslistFilterForm({ action, filters }: ProcesslistFilterFormProps) {
	return (
		<form
			action={action}
			className="grid gap-3 rounded-[1.2rem] border border-black/5 bg-[var(--panel)] p-4 md:grid-cols-3"
			method="get"
		>
			<TextInput
				defaultValue={filters.user}
				label="User"
				name="user"
				placeholder="e.g. root"
			/>
			<TextInput
				defaultValue={filters.host}
				label="Host"
				name="host"
				placeholder="e.g. 10.0.0.12"
			/>
			<TextInput
				defaultValue={filters.command}
				label="Command"
				name="command"
				placeholder="e.g. Query"
			/>
			<TextInput
				defaultValue={filters.minTimeSeconds}
				inputMode="numeric"
				label="Min time (s)"
				name="minTimeSeconds"
				placeholder="0"
			/>
			<TextInput
				defaultValue={filters.collectedAfter}
				label="Collected after"
				name="collectedAfter"
				placeholder="ISO 8601"
			/>
			<TextInput
				defaultValue={filters.collectedBefore}
				label="Collected before"
				name="collectedBefore"
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
		<label className="grid gap-1 text-sm" htmlFor={`processlist-${name}`}>
			<span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">
				{label}
			</span>
			<input
				className="rounded-[0.9rem] border border-black/10 bg-white px-3 py-2 text-sm text-[var(--ink)]"
				defaultValue={defaultValue}
				id={`processlist-${name}`}
				inputMode={inputMode}
				name={name}
				placeholder={placeholder}
				type="text"
			/>
		</label>
	);
}
