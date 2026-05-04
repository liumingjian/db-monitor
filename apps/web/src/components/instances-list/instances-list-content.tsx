"use client";

import type { InstanceResponse } from "@db-monitor/api-client";
import { useState } from "react";

import { CreateInstanceDrawer } from "./create-instance-drawer";
import { InstancesEmptyState } from "./instances-empty-state";
import { InstancesFilterChips } from "./instances-filter-chips";
import { InstancesGrid } from "./instances-grid";
import { InstancesTable } from "./instances-table";
import { InstancesToolbar } from "./instances-toolbar";
import { Slice2Banner } from "./slice2-banner";
import { BulkTier3Placeholders } from "./tier3-placeholder-actions";
import type { InstancesViewKey, SparkMetricKey, SparkValuesMap } from "./types";

const SPARK_COLOR_INDEX_BY_METRIC: Record<SparkMetricKey, number> = {
	connections: 1,
	qps: 2,
	active: 3,
};

interface InstancesListContentProps {
	readonly rows: readonly InstanceResponse[];
	readonly totalInstances: number;
	readonly filters: {
		readonly name: string;
		readonly environment: string;
		readonly label: string;
		readonly status: string;
	};
	readonly view: InstancesViewKey;
	readonly sparkMetric: SparkMetricKey;
	readonly sparkValues: SparkValuesMap;
}

export function InstancesListContent(props: InstancesListContentProps) {
	const { rows, totalInstances, filters, view, sparkMetric, sparkValues } = props;
	const [drawerOpen, setDrawerOpen] = useState(false);
	const sparkColorIndex = SPARK_COLOR_INDEX_BY_METRIC[sparkMetric];

	const hasAnyInstance = totalInstances > 0;
	const filteredEmpty = hasAnyInstance && rows.length === 0;
	const firstRun = !hasAnyInstance;

	return (
		<div className="flex flex-col gap-4">
			<InstancesFilterChips initial={filters} resultCount={rows.length} />
			<InstancesToolbar
				onOpenCreate={() => setDrawerOpen(true)}
				sparkMetric={sparkMetric}
				view={view}
			/>
			<BulkTier3Placeholders />
			{firstRun ? (
				<InstancesEmptyState onOpenCreate={() => setDrawerOpen(true)} reason="first-run" />
			) : filteredEmpty ? (
				<InstancesEmptyState onOpenCreate={() => setDrawerOpen(true)} reason="filtered" />
			) : view === "grid" ? (
				<InstancesGrid
					rows={rows}
					sparkColorIndex={sparkColorIndex}
					sparkMetric={sparkMetric}
					sparkValues={sparkValues}
				/>
			) : (
				<InstancesTable
					rows={rows}
					sparkColorIndex={sparkColorIndex}
					sparkMetric={sparkMetric}
					sparkValues={sparkValues}
				/>
			)}
			<Slice2Banner />
			<CreateInstanceDrawer onOpenChange={setDrawerOpen} open={drawerOpen} />
		</div>
	);
}
