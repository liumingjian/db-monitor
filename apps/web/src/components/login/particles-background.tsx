/**
 * CSS-only particle / aurora background for the Login brand panel.
 *
 * Design rules (ADR-0012 D7 + Q16 #10 #11 #12):
 *   - No JS animation, no canvas, no svg animation — pure CSS `@keyframes` +
 *     `radial-gradient` + transform/opacity on pseudo-free plain <span> layers.
 *   - Colors come exclusively from tokens.css CSS vars so both themes work.
 *   - No glassmorphism, no spinning circles, no purple gradient.
 *
 * Keyframes are scoped via a component-local <style> block keyed by a stable
 * class name prefix (`dbm-login-particles`) to avoid leaking into globals.
 */

const PARTICLE_STYLE = `
.dbm-login-particles {
	position: absolute;
	inset: 0;
	overflow: hidden;
	pointer-events: none;
	z-index: 0;
}
.dbm-login-particles::before,
.dbm-login-particles::after {
	content: "";
	position: absolute;
	inset: -20%;
	background:
		radial-gradient(closest-side, var(--accent-glow), transparent 70%) 15% 25% / 40% 40% no-repeat,
		radial-gradient(closest-side, var(--sev-info-bg), transparent 70%) 80% 15% / 35% 35% no-repeat,
		radial-gradient(closest-side, var(--sev-ok-bg), transparent 70%) 70% 80% / 40% 40% no-repeat,
		radial-gradient(closest-side, var(--sev-warning-bg), transparent 70%) 10% 85% / 30% 30% no-repeat;
	filter: blur(40px);
	opacity: 0.85;
	animation: dbm-login-drift 22s var(--ease-standard) infinite alternate;
}
.dbm-login-particles::after {
	background:
		radial-gradient(closest-side, var(--sev-info-bg), transparent 70%) 30% 70% / 45% 45% no-repeat,
		radial-gradient(closest-side, var(--accent-glow), transparent 70%) 90% 60% / 30% 30% no-repeat,
		radial-gradient(closest-side, var(--sev-ok-bg), transparent 70%) 55% 20% / 30% 30% no-repeat;
	filter: blur(60px);
	opacity: 0.55;
	animation: dbm-login-drift 34s var(--ease-standard) infinite alternate-reverse;
}
.dbm-login-particles > .dbm-login-dot {
	position: absolute;
	width: 6px;
	height: 6px;
	border-radius: 999px;
	background: var(--accent);
	box-shadow: 0 0 20px var(--accent-glow);
	opacity: 0.6;
	animation: dbm-login-float 9s var(--ease-standard) infinite alternate;
}
.dbm-login-particles > .dbm-login-dot.two {
	background: var(--sev-info);
	box-shadow: 0 0 18px var(--sev-info-bg);
	animation-duration: 13s;
}
.dbm-login-particles > .dbm-login-dot.three {
	background: var(--sev-ok);
	box-shadow: 0 0 18px var(--sev-ok-bg);
	animation-duration: 17s;
}
.dbm-login-particles > .dbm-login-dot.four {
	background: var(--sev-warning);
	box-shadow: 0 0 16px var(--sev-warning-bg);
	animation-duration: 21s;
}
@keyframes dbm-login-drift {
	0%   { transform: translate3d(-2%, -1%, 0) scale(1); }
	50%  { transform: translate3d(2%, 2%, 0) scale(1.05); }
	100% { transform: translate3d(-1%, 1%, 0) scale(1.02); }
}
@keyframes dbm-login-float {
	0%   { transform: translate3d(0, 0, 0); opacity: 0.3; }
	50%  { transform: translate3d(10px, -14px, 0); opacity: 0.75; }
	100% { transform: translate3d(-8px, 12px, 0); opacity: 0.4; }
}
@media (prefers-reduced-motion: reduce) {
	.dbm-login-particles::before,
	.dbm-login-particles::after,
	.dbm-login-particles > .dbm-login-dot { animation: none; }
}
`;

export function ParticlesBackground() {
	return (
		<div aria-hidden="true" className="dbm-login-particles">
			{/* biome-ignore lint/security/noDangerouslySetInnerHtml: static, author-controlled CSS string. */}
			<style dangerouslySetInnerHTML={{ __html: PARTICLE_STYLE }} />
			<span className="dbm-login-dot" style={{ top: "18%", left: "22%" }} />
			<span className="dbm-login-dot two" style={{ top: "34%", left: "68%" }} />
			<span className="dbm-login-dot three" style={{ top: "72%", left: "30%" }} />
			<span className="dbm-login-dot four" style={{ top: "58%", left: "78%" }} />
		</div>
	);
}
