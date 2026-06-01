# Focus Group Video Review Loop

## Goal

Build a self-improving video editing loop that uses a generated focus group to review a video, aggregate feedback, edit the video, and repeat until the aggregate score crosses an acceptance threshold.

## End-to-End Flow

1. The user provides a focus group description and a video.
2. The persona creation agent generates a diverse set of focus group personas from the description.
3. Each persona becomes a review agent with its own system prompt.
4. The video is sent to each persona review agent.
5. Each persona returns a review and score from its assigned perspective.
6. The system aggregates all persona reviews into a unified edit suggestion.
7. If the aggregate score crosses the acceptance threshold, the loop stops and returns the final video path plus the review summary history.
8. If the aggregate score does not cross the threshold, the video is edited from the aggregate suggestion and reviewed again.
9. The loop stops if the acceptance threshold is crossed or the maximum edit attempt count is reached.

## Current Scope

The current implementation focuses only on the first agent type: creating focus group personas from a focus group description.

The persona creation agent must:

- Produce exactly the requested number of personas.
- Create personas that are diverse in motivations, constraints, prior knowledge, expectations, skepticism, accessibility needs, and decision criteria.
- Generate one complete system prompt per persona.
- Make each persona useful for later video review and scoring.
- Avoid generic, duplicated, or purely demographic personas.

## Persistence And Observability

Phoenix is intended to be the SQL-backed persistence and observability layer. The application should store references through Phoenix span ids rather than adding a separate database layer.

Cloudflare R2 is intended to store video and file objects.

Events should be used to surface real-time progress to the UI, including focus group feedback gathering, aggregate threshold decisions, video edit attempts, edit success or failure, and edit attempt counter increments.

## Validation

The persona creation step has two immediate validation checks:

- Static assertion: generated persona count must match the requested focus group count.
- LLM judge, later: score the diversity and usefulness of the generated persona set.
