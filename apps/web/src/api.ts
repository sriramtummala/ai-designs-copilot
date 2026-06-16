const API_BASE = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://127.0.0.1:8000';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface WorkflowCreateRequest {
  page_type: string;
  audience: string;
  brand: string;
  channel: string;
  notes?: string;
}

export interface HistoryEntry {
  state: string;
  timestamp: string;
  reason?: string;
}

export interface WorkflowStatus {
  workflow_id: string;
  current_state: string;
  is_terminal: boolean;
  awaiting_human_review: boolean;
  history: HistoryEntry[];
  metadata: Record<string, unknown>;
  agent_output?: string;
  error?: { failed_at_state: string; reason: string };
}

// ── Helpers ───────────────────────────────────────────────────────────────────

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    const msg = typeof detail.detail === 'string'
      ? detail.detail
      : JSON.stringify(detail.detail ?? detail);
    throw new Error(msg || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── API calls ─────────────────────────────────────────────────────────────────

export const createWorkflow = (req: WorkflowCreateRequest) =>
  post<WorkflowStatus>('/workflows', req);

export const transitionWorkflow = (id: string, newState: string, reason = '') =>
  post<WorkflowStatus>(`/workflows/${id}/transition`, { new_state: newState, reason });

export const submitHumanReview = (id: string, approved: boolean, feedback = '') =>
  post<WorkflowStatus>(`/workflows/${id}/human-review`, { approved, feedback });
