"use client";

import { useRef, useState } from "react";

import type {
  AgentState,
  ContentReview,
} from "@/lib/types";
import {
  collectAnnotations,
  computeAggregateStats,
  formatTimestamp,
  type AnnotationWithPersona,
} from "@/lib/aggregate";

interface VideoReviewPanelProps {
  state: AgentState;
  videoUrl: string | null;
}

export function VideoReviewPanel({ state, videoUrl }: VideoReviewPanelProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [activeAnnotationIdx, setActiveAnnotationIdx] = useState<number | null>(
    null,
  );

  const annotations = collectAnnotations(state);

  function seekToAnnotation(ann: AnnotationWithPersona) {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = ann.timestamp_sec;
    void video.play().catch(() => {});
  }

  function handleTimelineClick(e: React.MouseEvent<HTMLDivElement>) {
    const video = videoRef.current;
    if (!video || duration === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pct = (e.clientX - rect.left) / rect.width;
    video.currentTime = pct * duration;
  }

  const activeAnnotation =
    activeAnnotationIdx !== null ? annotations[activeAnnotationIdx] : null;

  return (
    <div className="flex flex-col gap-4 lg:flex-row">
      <div className="flex-1 min-w-0">
        <div className="overflow-hidden rounded-xl border border-neutral-200 bg-black dark:border-neutral-800">
          {videoUrl ? (
            <video
              ref={videoRef}
              src={videoUrl}
              controls
              className="aspect-video w-full bg-black"
              onLoadedMetadata={(e) =>
                setDuration(e.currentTarget.duration || 0)
              }
              onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
            />
          ) : (
            <div className="flex aspect-video w-full items-center justify-center text-sm text-neutral-500">
              Video unavailable
            </div>
          )}
        </div>

        {videoUrl && duration > 0 && annotations.length > 0 && (
          <Timeline
            duration={duration}
            currentTime={currentTime}
            annotations={annotations}
            activeIdx={activeAnnotationIdx}
            onMarkerClick={(idx) => {
              setActiveAnnotationIdx(idx);
              seekToAnnotation(annotations[idx]);
            }}
            onTimelineClick={handleTimelineClick}
          />
        )}

        {activeAnnotation && (
          <div className="mt-3 rounded-lg border border-blue-200 bg-blue-50 p-3 dark:border-blue-900 dark:bg-blue-950/30">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-blue-700 dark:text-blue-400">
                {activeAnnotation.persona_name} @{" "}
                {formatTimestamp(activeAnnotation.timestamp_sec)}
              </span>
              <span className="text-xs font-bold text-blue-700 dark:text-blue-400">
                {activeAnnotation.score}/10
              </span>
            </div>
            <p className="mt-1 text-sm text-neutral-700 dark:text-neutral-300">
              {activeAnnotation.comment}
            </p>
          </div>
        )}
      </div>

      <aside className="flex w-full flex-col gap-4 lg:w-96">
        <AggregateStatsBlock state={state} />

        <section className="flex flex-col gap-2">
          <div className="flex items-baseline justify-between">
            <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
              Annotations
            </h3>
            {annotations.length > 0 && (
              <span className="text-xs text-neutral-400">
                {annotations.length}{" "}
                {annotations.length === 1 ? "marker" : "markers"}
              </span>
            )}
          </div>

          {annotations.length === 0 ? (
            <p className="text-xs text-neutral-400">
              {state.is_complete
                ? "No annotations were produced."
                : "Waiting for reviewers…"}
            </p>
          ) : (
            <ul className="flex flex-col gap-2">
              {annotations.map((ann, idx) => {
                const isActive = activeAnnotationIdx === idx;
                return (
                  <li key={`${ann.persona_id}-${ann.timestamp_sec}-${idx}`}>
                    <button
                      onClick={() => {
                        setActiveAnnotationIdx(idx);
                        seekToAnnotation(ann);
                      }}
                      className={[
                        "w-full rounded-lg border p-3 text-left transition-colors",
                        isActive
                          ? "border-blue-400 bg-blue-50 dark:border-blue-700 dark:bg-blue-950/30"
                          : "border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50 dark:border-neutral-800 dark:hover:border-neutral-700 dark:hover:bg-neutral-900",
                      ].join(" ")}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
                          {ann.persona_name}
                        </span>
                        <span className="text-xs font-mono text-neutral-500">
                          {formatTimestamp(ann.timestamp_sec)}
                        </span>
                      </div>
                      <p className="mt-1 text-xs leading-relaxed text-neutral-600 dark:text-neutral-400">
                        {ann.comment}
                      </p>
                      <span className="mt-1.5 inline-block rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] font-bold text-neutral-600 dark:bg-neutral-800 dark:text-neutral-400">
                        {ann.score}/10
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <ReviewsByPersona state={state} />
      </aside>
    </div>
  );
}

function Timeline({
  duration,
  currentTime,
  annotations,
  activeIdx,
  onMarkerClick,
  onTimelineClick,
}: {
  duration: number;
  currentTime: number;
  annotations: AnnotationWithPersona[];
  activeIdx: number | null;
  onMarkerClick: (idx: number) => void;
  onTimelineClick: (e: React.MouseEvent<HTMLDivElement>) => void;
}) {
  return (
    <div className="mt-3">
      <div
        className="relative h-8 w-full cursor-pointer rounded bg-neutral-100 dark:bg-neutral-900"
        onClick={onTimelineClick}
      >
        <div
          className="absolute top-0 left-0 h-full rounded bg-blue-200/40 dark:bg-blue-800/40"
          style={{ width: `${(currentTime / duration) * 100}%` }}
        />
        {annotations.map((ann, idx) => {
          const pct = (ann.timestamp_sec / duration) * 100;
          const isActive = activeIdx === idx;
          const hue = scoreToHue(ann.score);
          return (
            <button
              key={`${ann.persona_id}-${ann.timestamp_sec}-${idx}`}
              onClick={(e) => {
                e.stopPropagation();
                onMarkerClick(idx);
              }}
              title={`${ann.persona_name} @ ${formatTimestamp(
                ann.timestamp_sec,
              )}: ${ann.comment}`}
              className={[
                "absolute top-1/2 -translate-y-1/2 -translate-x-1/2 rounded-full transition-transform",
                isActive
                  ? "h-4 w-4 ring-2 ring-blue-500 ring-offset-1 dark:ring-offset-neutral-900"
                  : "h-3 w-3 hover:scale-125",
              ].join(" ")}
              style={{
                left: `${pct}%`,
                backgroundColor: `hsl(${hue}, 70%, 50%)`,
              }}
            />
          );
        })}
      </div>
      <div className="mt-1 flex justify-between text-[10px] font-mono text-neutral-400">
        <span>0:00</span>
        <span>{formatTimestamp(duration)}</span>
      </div>
    </div>
  );
}

function AggregateStatsBlock({ state }: { state: AgentState }) {
  const stats = computeAggregateStats(state);

  if (state.reviews.length === 0) {
    return null;
  }

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-neutral-200 p-4 dark:border-neutral-800">
      <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
        Aggregate stats
      </h3>

      {stats.overallRating !== null && (
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold">
            {stats.overallRating.toFixed(1)}
          </span>
          <span className="text-sm text-neutral-400">overall / 10</span>
        </div>
      )}

      <div className="flex flex-col gap-2">
        {stats.perQuestion.map((qs) => (
          <div
            key={qs.question.id}
            className="flex flex-col gap-1 border-t border-neutral-100 pt-2 dark:border-neutral-900"
          >
            <span className="text-xs font-medium text-neutral-700 dark:text-neutral-300">
              {qs.question.question}
            </span>
            {qs.avgScore !== null ? (
              <div className="flex items-center gap-2">
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-900">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${(qs.avgScore / 10) * 100}%`,
                      backgroundColor: `hsl(${scoreToHue(qs.avgScore)}, 70%, 50%)`,
                    }}
                  />
                </div>
                <span className="text-xs font-mono font-bold">
                  {qs.avgScore.toFixed(1)}
                </span>
                <span className="text-xs text-neutral-400">
                  ({qs.responses.length}{" "}
                  {qs.responses.length === 1 ? "resp" : "resps"})
                </span>
              </div>
            ) : (
              <span className="text-xs text-neutral-400">
                No responses yet
              </span>
            )}
          </div>
        ))}
      </div>

      {stats.totalAnnotations > 0 && stats.avgAnnotationScore !== null && (
        <div className="flex items-center justify-between border-t border-neutral-100 pt-2 dark:border-neutral-900">
          <span className="text-xs text-neutral-500">Annotation avg</span>
          <span className="text-xs font-mono font-bold">
            {stats.avgAnnotationScore.toFixed(1)}/10
          </span>
        </div>
      )}
    </section>
  );
}

function ReviewsByPersona({ state }: { state: AgentState }) {
  if (state.reviews.length === 0) return null;
  const personaMap = new Map(state.personas.map((p) => [p.id, p.name]));

  return (
    <section className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold tracking-wide text-neutral-500 uppercase dark:text-neutral-400">
        Reviews by persona
      </h3>
      <ul className="flex flex-col gap-3">
        {state.reviews.map((review) => (
          <li key={review.persona_id}>
            <PersonaReview
              review={review}
              personaName={
                personaMap.get(review.persona_id) ?? review.persona_id
              }
              questions={state.agent_input?.questions ?? []}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

function PersonaReview({
  review,
  personaName,
  questions,
}: {
  review: ContentReview;
  personaName: string;
  questions: { id: string; question: string }[];
}) {
  return (
    <div className="rounded-lg border border-neutral-200 p-3 dark:border-neutral-800">
      <span className="text-xs font-semibold">{personaName}</span>
      <ul className="mt-2 flex flex-col gap-1.5">
        {review.answers.map((ans) => {
          const q = questions.find((q) => q.id === ans.question_id);
          return (
            <li key={ans.question_id} className="flex flex-col gap-0.5">
              <span className="text-[11px] font-medium text-neutral-500">
                {q?.question ?? ans.question_id}
              </span>
              <span className="text-xs text-neutral-700 dark:text-neutral-300">
                {ans.answer}
              </span>
              <span className="text-[10px] font-mono text-neutral-400">
                {ans.score}/10
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function scoreToHue(score: number): number {
  const clamped = Math.max(1, Math.min(10, score));
  return (clamped - 1) * 20;
}