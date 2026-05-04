import { PageContent } from "@db-monitor/ui";

import { Tier3PlaceholderCard } from "../../../../src/components/instance-detail/tier3-placeholder-card";

// 复制 tab：Tier 3 honest placeholder.
// 后端尚未开放 replication topology / lag history 端点，能力即将上线。
export default function ReplicationPlaceholderPage() {
	return (
		<PageContent>
			<Tier3PlaceholderCard
				capabilities={[
					"主从拓扑图（GTID / binlog file + position）",
					"复制延迟时间序列（Seconds_Behind_Master / standby_lag_seconds）",
					"复制错误码 + IO/SQL 线程状态监控",
					"异步故障切换记录",
				]}
				description="复制视图需要后端新增 replication topology 与 lag history 端点；与绑定写入能力一并上线。"
				statusLabel="即将上线"
				title="复制"
			/>
		</PageContent>
	);
}
