"use client";

import type { AgentState } from "@/lib/types";
import { Shimmer } from "./Shimmer";

interface ReviewGuidanceProps {
  state: AgentState;
}

export function ReviewGuidance({ state }: ReviewGuidanceProps) {
  const guidance = state.agent_input?.review_guidance;

  return (
    <section className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
        Reviewer guidance
      </h3>
      {guidance ? (
        <p className="text-sm leading-relaxed text-neutral-700 dark:text-neutral-300">
          {guidance}
        </p>
      ) : (
        <Shimmer className="h-12 w-full" />
      )}
    </section>
  );
}