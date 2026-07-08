"use client";

import { useEffect, useRef, useState } from "react";

import type { AgentState } from "@/lib/types";
import { invokeAgent, streamAgentStateUpdates } from "@/lib/api";
import { FileUpload } from "@/components/FileUpload";
import { PromptForm } from "@/components/PromptForm";
import { PersonasSection } from "@/components/PersonasSection";
import { ReviewGuidance } from "@/components/ReviewGuidance";
import { VideoReviewPanel } from "@/components/VideoReviewPanel";

type Stage = "upload" | "prompt" | "results";

export default function Home() {
  const [stage, setStage] = useState<Stage>("upload");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [contentCacheName, setContentCacheName] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  useEffect(() => {
    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
        objectUrlRef.current = null;
      }
    };
  }, []);

  function handleUploaded(file: File, cacheName: string) {
    setUploadedFile(file);
    setContentCacheName(cacheName);

    if (objectUrlRef.current) URL.revokeObjectURL(objectUrlRef.current);
    const url = URL.createObjectURL(file);
    objectUrlRef.current = url;
    setVideoUrl(url);

    setStage("prompt");
  }

  async function handlePromptSubmit(prompt: string) {
    if (!contentCacheName) return;
    setIsStarting(true);
    setError(null);
    setAgentState(null);

    try {
      const { run_id } = await invokeAgent(prompt, contentCacheName);

      setStage("results");
      setIsStarting(false);

      await streamAgentStateUpdates(run_id, {
        onState: (s) => {
          setAgentState((prev) =>
            prev
              ? {
                  ...prev,
                  ...s,
                  reviews: s.reviews.length > 0 ? s.reviews : prev.reviews,
                  personas: s.personas.length > 0 ? s.personas : prev.personas,
                }
              : s,
          );
        },
        onError: (err) => {
          setError(err.message);
          setIsStarting(false);
        },
        onComplete: () => {},
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to start the agent.",
      );
      setIsStarting(false);
    }
  }

  function reset() {
    setStage("upload");
    setUploadedFile(null);
    setContentCacheName(null);
    setVideoUrl(null);
    setAgentState(null);
    setError(null);
    setIsStarting(false);
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
  }

  return (
    <main className="flex min-h-dvh flex-col">
      <header className="flex items-center justify-between border-b border-neutral-200 px-6 py-4 dark:border-neutral-800">
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold tracking-tight">
            Focus Group Reviewer
          </span>
        </div>
        <div className="flex items-center gap-3 text-xs text-neutral-400">
          {uploadedFile && (
            <span className="hidden sm:inline font-mono">
              {uploadedFile.name}
            </span>
          )}
          {contentCacheName && stage !== "upload" && (
            <button
              onClick={reset}
              className="rounded-md border border-neutral-200 px-3 py-1.5 font-medium text-neutral-600 transition-colors hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-400 dark:hover:bg-neutral-900"
            >
              Start over
            </button>
          )}
        </div>
      </header>

      <div className="flex flex-1 items-center justify-center px-6 py-10">
        {error && (
          <div className="fixed top-4 right-4 z-50 max-w-sm rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 shadow-lg dark:border-red-900 dark:bg-red-950/50 dark:text-red-400" role="alert">
            <div className="flex items-start justify-between gap-2">
              <p>{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-red-400 hover:text-red-600"
                aria-label="Dismiss"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {stage === "upload" && <FileUpload onUploaded={handleUploaded} />}

        {stage === "prompt" && (
          <PromptForm onSubmit={handlePromptSubmit} isStarting={isStarting} />
        )}

        {stage === "results" && (
          <div className="mx-auto flex w-full max-w-5xl flex-col gap-8">
            {agentState ? (
              <>
                <div className="flex flex-col gap-6">
                  <ReviewGuidance state={agentState} />
                  <PersonasSection state={agentState} />
                </div>

                {agentState.reviews.length > 0 && (
                  <div className="border-t border-neutral-200 pt-6 dark:border-neutral-800">
                    <h2 className="mb-4 text-xl font-semibold tracking-tight">
                      Video &amp; reviews
                    </h2>
                    <VideoReviewPanel
                      state={agentState}
                      videoUrl={videoUrl}
                    />
                  </div>
                )}

                {!agentState.is_complete && (
                  <div className="flex items-center justify-center gap-2 text-sm text-neutral-500">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-500 dark:border-neutral-700 dark:border-t-blue-400" />
                    <span>Personas are reviewing the video…</span>
                  </div>
                )}
              </>
            ) : (
              <div className="flex flex-col items-center gap-4">
                <div className="h-10 w-10 animate-spin rounded-full border-2 border-neutral-300 border-t-blue-500 dark:border-neutral-700 dark:border-t-blue-400" />
                <p className="text-sm text-neutral-500">
                  Preparing your focus group…
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}