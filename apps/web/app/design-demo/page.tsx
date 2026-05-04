"use client";

import {
	AppShell,
	Badge,
	Button,
	CanonicalPageTemplate,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	EntityBadge,
	EntitySummary,
	Input,
	Label,
	PageBreadcrumb,
	PageContent,
	QuickMetrics,
	Separator,
	Skeleton,
	Switch,
	TabBar,
	ThemeToggle,
	TopBar,
} from "@db-monitor/ui";
import { formatBytes, formatDuration, formatPercent } from "@db-monitor/ui";

import { AppSidebar } from "../../src/components/shell/app-sidebar";

const tabs = [
	{ key: "primitives", label: "Primitives" },
	{ key: "formatters", label: "Formatters" },
	{ key: "severity", label: "严重度" },
] as const;

export default function DesignDemoPage() {
	return (
		<AppShell
			sidebar={<AppSidebar />}
			topBar={
				<TopBar
					breadcrumbs={[{ label: "观测", href: "/overview" }, { label: "设计系统 Demo" }]}
					commandLabel="搜索或跳转"
					commandShortcut="⌘K"
					notificationCount={2}
					notificationLabel="通知"
					onCommandOpen={() => {}}
					themeToggle={<ThemeToggle labelDark="切换到亮色主题" labelLight="切换到暗色主题" />}
					userAvatar={
						<div className="flex h-8 w-8 items-center justify-center rounded-full bg-accent/15 text-xs font-semibold text-accent">
							DB
						</div>
					}
				/>
			}
		>
			<CanonicalPageTemplate>
				<PageBreadcrumb
					items={[{ label: "观测", href: "/overview" }, { label: "设计系统 Demo" }]}
				/>
				<EntitySummary
					actions={
						<>
							<Button size="sm" variant="outline">
								查看 ADR-0016
							</Button>
							<Button size="sm" variant="default">
								继续开发
							</Button>
						</>
					}
					badges={[
						{ tone: "ok", label: "设计就绪" },
						{ tone: "info", label: "Slice 1.5b" },
					]}
					subtitle="验证 tokens / 字体 / 双主题 / primitives / layout / utils 协同"
					title="设计系统冒烟页"
				/>
				<QuickMetrics
					items={[
						{ key: "routes", label: "已覆盖路由", value: "11 / 14" },
						{ key: "tests", label: "单元测试", value: "104" },
						{ key: "p95", label: "构建耗时", value: formatDuration(2340) },
						{ key: "bundle", label: "首屏 JS", value: formatBytes(280000) },
						{ key: "coverage", label: "i18n 覆盖率", value: formatPercent(0.08) },
						{ key: "tokens", label: "CSS vars", value: "56" },
					]}
				/>
				<TabBar tabs={tabs} activeKey="primitives" />
				<PageContent>
					<div className="grid gap-6">
						<Card>
							<CardHeader>
								<CardTitle>Button 变体</CardTitle>
								<CardDescription>
									default / outline / ghost / destructive / link；三档尺寸
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="flex flex-wrap items-center gap-3">
									<Button>主要操作</Button>
									<Button variant="outline">次要</Button>
									<Button variant="ghost">Ghost</Button>
									<Button variant="destructive">删除</Button>
									<Button variant="link">链接风</Button>
									<Button size="sm">小号</Button>
									<Button size="lg">大号</Button>
								</div>
							</CardContent>
						</Card>

						<Card>
							<CardHeader>
								<CardTitle>严重度轴 / Badge</CardTitle>
								<CardDescription>
									critical / warning / info / ok — 四色统一到 tokens
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="flex flex-wrap items-center gap-3">
									<EntityBadge tone="critical" label="紧急" />
									<EntityBadge tone="warning" label="警告" />
									<EntityBadge tone="info" label="提示" />
									<EntityBadge tone="ok" label="健康" />
									<Separator className="h-6" orientation="vertical" />
									<Badge variant="default">Default</Badge>
									<Badge variant="outline">Outline</Badge>
									<Badge variant="secondary">Secondary</Badge>
									<Badge variant="destructive">Destructive</Badge>
								</div>
							</CardContent>
						</Card>

						<div className="grid gap-6 md:grid-cols-2">
							<Card>
								<CardHeader>
									<CardTitle>表单 primitives</CardTitle>
									<CardDescription>Input / Label / Switch</CardDescription>
								</CardHeader>
								<CardContent>
									<div className="flex flex-col gap-4">
										<div className="flex flex-col gap-1.5">
											<Label htmlFor="demo-username" required>
												用户名
											</Label>
											<Input id="demo-username" name="username" placeholder="admin" />
										</div>
										<div className="flex flex-col gap-1.5">
											<Label htmlFor="demo-threshold">阈值</Label>
											<Input
												defaultValue="0.85"
												id="demo-threshold"
												name="threshold"
												type="number"
											/>
										</div>
										<div className="flex items-center justify-between rounded-md border border-border-hairline bg-bg-elevated px-3 py-2">
											<Label htmlFor="demo-switch">启用规则</Label>
											<Switch defaultChecked id="demo-switch" />
										</div>
									</div>
								</CardContent>
							</Card>

							<Card>
								<CardHeader>
									<CardTitle>加载态 / Skeleton</CardTitle>
									<CardDescription>骨架屏，不使用 spinner</CardDescription>
								</CardHeader>
								<CardContent>
									<div className="flex flex-col gap-3">
										<Skeleton className="h-4 w-3/4" />
										<Skeleton className="h-4 w-full" />
										<Skeleton className="h-4 w-2/3" />
										<Separator />
										<Skeleton className="h-24 w-full rounded-md" />
									</div>
								</CardContent>
							</Card>
						</div>

						<Card>
							<CardHeader>
								<CardTitle>格式化函数样例</CardTitle>
								<CardDescription>
									formatBytes / formatDuration / formatPercent 走 mono 字体
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ul className="grid gap-2 font-mono text-sm tabular-nums text-fg-secondary">
									<li>formatBytes(1_234_567_890) = {formatBytes(1_234_567_890)}</li>
									<li>formatDuration(3_660_000) = {formatDuration(3_660_000)}</li>
									<li>formatPercent(0.8532) = {formatPercent(0.8532)}</li>
									<li>formatPercent(null) = {formatPercent(null)}</li>
								</ul>
							</CardContent>
						</Card>
					</div>
				</PageContent>
			</CanonicalPageTemplate>
		</AppShell>
	);
}
