export type RecommendationType = "study" | "discovery";

export interface Recommendation {
  type: RecommendationType;
  title: string;
  reason: string;
  evidence_ids: string[];
  action_target: string;
}