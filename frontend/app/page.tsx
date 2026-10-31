import TopBar from "@/components/TopBar";
import KnowledgeMap from "@/components/KnowledgeMap";
import recommendations from "@/data/due_task.json";
import { Recommendation } from "@/types/recommendation";

const recs = recommendations as Recommendation[];

export default function HomePage() {
  return (
    <div className="flex h-full flex-col gap-4">
      <TopBar />
      <KnowledgeMap recs={recs} />
    </div>
  );
}