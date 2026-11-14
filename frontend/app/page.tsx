"use client";

import TopBar from "@/components/TopBar";
import KnowledgeMap from "@/components/KnowledgeMap";
import { api, USE_FIXTURES } from "@/lib/api-client";
import { useApiData } from "@/lib/use-api-data";

export default function TodayPage() {
  // Runs POST /recommendations/generate when the page opens
  // (or reads the sample fixture when NEXT_PUBLIC_USE_FIXTURES=true)
  const recs = useApiData(api.generateRecommendations);

  return (
    <div className="flex h-full flex-col gap-4">
      <TopBar />
      <KnowledgeMap
        status={recs.status}
        recs={recs.data ?? []}
        errorMessage={recs.error?.message}
        onRefresh={recs.reload}
        isSample={USE_FIXTURES}
      />
    </div>
  );
}
