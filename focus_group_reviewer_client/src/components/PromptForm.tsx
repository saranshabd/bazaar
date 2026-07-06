"use client";

import { useState } from "react";

interface PromptFormProps {
  onSubmit: (prompt: string) => void;
  isStarting: boolean;
}

const EXAMPLE_PROMPTS = [
  {
    title: "Prestige TV drama fans",
    text: "I want feedback from young adults aged 18-30 who are fans of prestige TV dramas like Succession and The Bear. They should be critical viewers who pay attention to dialogue, character development, and pacing. Ask them: would they watch the next episode? What was the most memorable scene and why? Rate the overall pilot on a scale of 1-10.",
  },
  {
    title: "STEM students reviewing a lecture",
    text: "Create a diverse focus group of STEM college students who will review a video from different student perspectives. Include students across different majors, years, goals, technical confidence levels, learning styles, campus contexts, and levels of skepticism. The group should include people who care about clarity, practical usefulness, credibility, pacing, accessibility, visual explanation quality, and whether the video would hold their attention. Avoid making the personas differ only by major or demographics; each persona should have distinct motivations, constraints, and evaluation criteria.",
  },
  {
    title: "Casual comedy viewers",
    text: "I want feedback from casual comedy viewers aged 25-45 who watch sitcoms for relaxation and laughs. They should value humor, relatability, and pacing over prestige or artistic ambition. Ask them: did it make you laugh out loud? Would you recommend it to a friend? How does it compare to other comedies you enjoy?",
  },
];

export function PromptForm({ onSubmit, isStarting }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col gap-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold tracking-tight">
          Describe your focus group
        </h2>
        <p className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          Tell us who should review your video and what they should pay attention to.
          We&apos;ll generate a panel of personas and have each one review it.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {EXAMPLE_PROMPTS.map((ex) => (
          <button
            key={ex.title}
            type="button"
            onClick={() => setPrompt(ex.text)}
            className="rounded-full border border-neutral-200 px-3 py-1.5 text-xs font-medium text-neutral-600 transition-colors hover:border-neutral-300 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-400 dark:hover:border-neutral-600 dark:hover:bg-neutral-900"
          >
            {ex.title}
          </button>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (prompt.trim() && !isStarting) onSubmit(prompt.trim());
        }}
        className="flex flex-col gap-4"
      >
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g. I want feedback from young adults aged 18-30 who are fans of prestige TV dramas like Succession and The Bear. They should be critical viewers who pay attention to dialogue, character development, and pacing. Ask them: would they watch the next episode? What was the most memorable scene and why? Rate the overall pilot on a scale of 1-10."
          rows={6}
          className="w-full resize-none rounded-xl border border-neutral-200 bg-transparent px-4 py-3 text-sm leading-relaxed outline-none transition-colors placeholder:text-neutral-400 focus:border-blue-500 dark:border-neutral-700 dark:placeholder:text-neutral-500"
        />

        <div className="flex items-center justify-between">
          <p className="text-xs text-neutral-400">
            {prompt.length > 0
              ? `${prompt.length} characters`
              : "Pick a suggestion above or write your own."}
          </p>
          <button
            type="submit"
            disabled={!prompt.trim() || isStarting}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            {isStarting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Starting…
              </>
            ) : (
              "Let\u2019s go"
            )}
          </button>
        </div>
      </form>
    </div>
  );
}