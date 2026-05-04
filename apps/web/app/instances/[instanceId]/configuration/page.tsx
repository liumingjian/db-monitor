import { PageContent } from "@db-monitor/ui";

import { Tier3PlaceholderCard } from "../../../../src/components/instance-detail/tier3-placeholder-card";

/**
 * Q13 配置 tab：Tier 3 honest placeholder。
 * 后端尚未开放 per-instance parameter / SHOW VARIABLES 端点，预计 Slice 2 交付。
 */
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
				description="配置视图需要后端新增 parameter snapshot / baseline 端点；预计 Slice 2 上线，与 Slice 2 的 PostgresBindingRepository 落地同步。"
				sliceLabel="Slice 2 交付"
				title="配置"
			/>
		</PageContent>
	);
}
