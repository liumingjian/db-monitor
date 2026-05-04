import { PageContent } from "@db-monitor/ui";

import { Tier3PlaceholderCard } from "../../../../src/components/instance-detail/tier3-placeholder-card";

// 配置 tab：Tier 3 honest placeholder.
// 后端尚未开放 per-instance parameter / SHOW VARIABLES 端点，能力即将上线。
export default function ConfigurationPlaceholderPage() {
	return (
		<PageContent>
			<Tier3PlaceholderCard
				capabilities={[
					"MySQL SHOW VARIABLES / SHOW STATUS diff 比较",
					"Oracle v$parameter 基线对照",
					"按模板（OLTP / OLAP / Replica）定义推荐参数",
					"与运行值漂移告警",
				]}
				description="配置视图需要后端新增 parameter snapshot / baseline 端点；与绑定写入能力一并上线。"
				statusLabel="即将上线"
				title="配置"
			/>
		</PageContent>
	);
}
