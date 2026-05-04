import { redirect } from "next/navigation";

import { LoginShell } from "../../src/components/login/login-shell";
import { fetchServerSession } from "../../src/server-api";

const DEFAULT_NEXT_PATH = "/overview";

interface LoginPageProps {
	readonly searchParams: Promise<{
		readonly next?: string;
	}>;
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
	const session = await fetchServerSession();
	if (session !== null) {
		redirect(DEFAULT_NEXT_PATH);
	}
	const params = await searchParams;
	const nextPath = params.next ?? DEFAULT_NEXT_PATH;
	return <LoginShell nextPath={nextPath} />;
}
