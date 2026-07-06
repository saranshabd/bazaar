import type {
  AgentState,
  Annotation,
  Question,
  QuestionResponse,
} from "./types";

export interface QuestionStat {
  question: Question;
  scores: number[];
  avgScore: number | null;
  responses: { persona_id: string; persona_name: string; answer: QuestionResponse }[];
}

export interface AggregateStats {
  perQuestion: QuestionStat[];
  overallRating: number | null;
  totalAnnotations: number;
  avgAnnotationScore: number | null;
}

export function computeAggregateStats(state: AgentState): AggregateStats {
  const personaMap = new Map(state.personas.map((p) => [p.id, p.name]));
  const reviews = state.reviews;
  const questions = state.agent_input?.questions ?? [];

  const perQuestion: QuestionStat[] = questions.map((question) => {
    const responses: QuestionStat["responses"] = [];

    for (const review of reviews) {
      const ans = review.answers.find((a) => a.question_id === question.id);
      if (ans) {
        responses.push({
          persona_id: review.persona_id,
          persona_name: personaMap.get(review.persona_id) ?? review.persona_id,
          answer: ans,
        });
      }
    }

    const scores = responses.map((r) => r.answer.score);
    const avgScore =
      scores.length > 0
        ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10
        : null;

    return { question, scores, avgScore, responses };
  });

  const allAnswerScores = reviews.flatMap((r) =>
    r.answers.map((a) => a.score),
  );
  const overallRating =
    allAnswerScores.length > 0
      ? Math.round(
          (allAnswerScores.reduce((a, b) => a + b, 0) / allAnswerScores.length) *
            10,
        ) / 10
      : null;

  const allAnnotations: Annotation[] = reviews.flatMap((r) => r.annotations);
  const annotationScores = allAnnotations.map((a) => a.score);
  const avgAnnotationScore =
    annotationScores.length > 0
      ? Math.round(
          (annotationScores.reduce((a, b) => a + b, 0) /
            annotationScores.length) *
            10,
        ) / 10
      : null;

  return {
    perQuestion,
    overallRating,
    totalAnnotations: allAnnotations.length,
    avgAnnotationScore,
  };
}

export interface AnnotationWithPersona extends Annotation {
  persona_id: string;
  persona_name: string;
}

export function collectAnnotations(state: AgentState): AnnotationWithPersona[] {
  const personaMap = new Map(state.personas.map((p) => [p.id, p.name]));
  const all: AnnotationWithPersona[] = [];

  for (const review of state.reviews) {
    for (const ann of review.annotations) {
      all.push({
        ...ann,
        persona_id: review.persona_id,
        persona_name: personaMap.get(review.persona_id) ?? review.persona_id,
      });
    }
  }

  return all.sort((a, b) => a.timestamp_sec - b.timestamp_sec);
}

export function formatTimestamp(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60);
  const s = Math.floor(totalSeconds % 60);
  const padded = s.toString().padStart(2, "0");
  return `${m}:${padded}`;
}