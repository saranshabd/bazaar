import type { AgentState } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:9384";

export async function cacheVideo(
  file: File,
): Promise<{ cache_name: string }> {
  const formData = new FormData();
  formData.append("video", file);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000);

  let res: Response;
  try {
    res = await fetch(`${API_BASE}/content/cache-video`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("cacheVideo timed out after 5 minutes");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`cacheVideo failed (${res.status}): ${text}`);
  }

  return res.json() as Promise<{ cache_name: string }>;
}

export async function invokeAgent(
  userPrompt: string,
  contentCacheName: string,
): Promise<{ run_id: string }> {
  const params = new URLSearchParams({
    user_prompt: userPrompt,
    content_cache_name: contentCacheName,
  });

  const res = await fetch(`${API_BASE}/agent/invoke?${params.toString()}`, {
    method: "POST",
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`invokeAgent failed (${res.status}): ${text}`);
  }

  return res.json() as Promise<{ run_id: string }>;
}

export interface StreamHandlers {
  onState: (state: AgentState) => void;
  onError: (err: Error) => void;
  onComplete: () => void;
}

export async function streamAgentStateUpdates(
  runId: string,
  handlers: StreamHandlers,
): Promise<void> {
  const { onState, onError, onComplete } = handlers;
  const url = `${API_BASE}/agent/state/updates?run_id=${encodeURIComponent(runId)}`;

  let res: Response;
  try {
    res = await fetch(url, { headers: { Accept: "text/event-stream" } });
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
    return;
  }

  if (!res.ok || !res.body) {
    onError(new Error(`SSE connection failed (${res.status})`));
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split("\n\n");
      buffer = parts.pop() ?? "";

      for (const part of parts) {
        const lines = part.split("\n");
        let dataStr = "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            dataStr += line.slice(5).trim();
          } else if (line.startsWith("event:")) {
            const evt = line.slice(6).trim();
            if (evt === "error" || evt === "close") {
              console.warn(`SSE terminal event: ${evt}`);
            }
          }
        }

        if (!dataStr || dataStr === "[DONE]") continue;

        try {
          const parsed = JSON.parse(dataStr) as AgentState;
          onState(parsed);
          if (parsed.is_complete) {
            onComplete();
            return;
          }
        } catch (err) {
          console.error("Failed to parse SSE state payload", err, dataStr);
        }
      }
    }
  } catch (err) {
    onError(err instanceof Error ? err : new Error(String(err)));
    return;
  }

  onComplete();
}