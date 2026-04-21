import { LOGIN_FORM_FIELDS } from "@db-monitor/ui";
import { redirect } from "next/navigation";

import { fetchServerSession } from "../../src/server-api";

interface LoginPageProps {
	readonly searchParams: Promise<{
		readonly next?: string;
	}>;
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
	const session = await fetchServerSession();
	if (session !== null) {
		redirect("/overview");
	}
	const params = await searchParams;

	return (
		<div className="mx-auto flex min-h-screen max-w-3xl items-center px-6 py-10">
			<section className="w-full rounded-[2rem] border border-black/10 bg-white/80 p-8 shadow-[0_24px_80px_rgba(15,23,42,0.08)] backdrop-blur">
				<p className="text-xs font-semibold uppercase tracking-[0.28em] text-[var(--accent)]">
					Session Access
				</p>
				<h1 className="mt-4 text-4xl font-semibold leading-tight">Enter the operations shell</h1>
				<p className="mt-3 max-w-xl text-sm leading-6 text-[var(--muted)]">
					Authentication stays on the API boundary. The web shell only coordinates the route guard,
					typed client, and shared providers.
				</p>
				<form action="/api/login" className="mt-8 grid gap-4" method="post">
					<input name="next" type="hidden" value={params.next ?? "/overview"} />
					{LOGIN_FORM_FIELDS.map((field) => (
						<label className="grid gap-2" htmlFor={field.name} key={field.name}>
							<span className="text-sm font-medium">{field.label}</span>
							<input
								className="rounded-[1rem] border border-black/10 bg-[var(--panel)] px-4 py-3 outline-none transition focus:border-[var(--accent)]"
								id={field.name}
								name={field.name}
								placeholder={field.placeholder}
								type={field.type}
							/>
						</label>
					))}
					<button
						className="mt-2 rounded-[1rem] bg-[var(--accent)] px-5 py-3 text-sm font-semibold text-white"
						type="submit"
					>
						Sign in
					</button>
				</form>
			</section>
		</div>
	);
}
