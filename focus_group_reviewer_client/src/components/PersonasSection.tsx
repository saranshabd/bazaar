"use client";

import type { AgentState, Persona } from "@/lib/types";
import { Shimmer } from "./Shimmer";

interface PersonasSectionProps {
  state: AgentState;
}

export function PersonasSection({ state }: PersonasSectionProps) {
  const { agent_input, personas } = state;
  const expectedCount = agent_input?.persona_count ?? 0;
  const hasPersonas = personas.length > 0;

  if (!agent_input) {
    return (
      <section className="flex flex-col gap-3">
        <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
          Focus group
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Shimmer className="h-32 w-full" />
          <Shimmer className="h-32 w-full" />
        </div>
      </section>
    );
  }

  const placeholdersNeeded = hasPersonas ? 0 : Math.max(expectedCount, 2);

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
          Focus group
        </h3>
        {hasPersonas && (
          <span className="text-xs text-neutral-400">
            {personas.length} {personas.length === 1 ? "persona" : "personas"}
          </span>
        )}
      </div>

      <p className="text-sm text-neutral-600 dark:text-neutral-300">
        {agent_input.focus_group_description}
      </p>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {hasPersonas
          ? personas.map((p) => <PersonaCard key={p.id} persona={p} />)
          : Array.from({ length: placeholdersNeeded }).map((_, i) => (
              <Shimmer key={i} className="h-32 w-full" />
            ))}
      </div>
    </section>
  );
}

function PersonaCard({ persona }: { persona: Persona }) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
      <div className="flex items-center gap-2">
        <div className="flex h-9 w-9 items-center justify-center rounded-full bg-neutral-100 text-sm font-semibold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300">
          {persona.name.charAt(0).toUpperCase()}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-semibold">{persona.name}</span>
          <span className="text-xs text-neutral-400">{persona.demographics}</span>
        </div>
      </div>
      <p className="text-xs leading-relaxed text-neutral-600 dark:text-neutral-400">
        {persona.bio}
      </p>
    </div>
  );
}