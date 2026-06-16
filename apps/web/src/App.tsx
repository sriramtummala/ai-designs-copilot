import { useState } from 'react';
import { Button, Card, Alert, PageSection } from '@ai-designops/ui';
import '@ai-designops/tokens/theme.css';
import './App.css';
import DsComparison from './DsComparison';
import {
  createWorkflow,
  transitionWorkflow,
  submitHumanReview,
  type WorkflowStatus,
} from './api';

// ── Types ─────────────────────────────────────────────────────────────────────

type AppView = 'form' | 'tokens';

interface FormData {
  pageType: string;
  audience: string;
  brand: string;
  channel: string;
  notes: string;
}

type WorkflowPhase = 'running' | 'human_review' | 'completed' | 'failed';

interface ActiveWorkflow {
  id: string;
  phase: WorkflowPhase;
  step: string;
  status?: WorkflowStatus;
  error?: string;
}

const STEPS = [
  { key: 'create',  label: 'Create workflow' },
  { key: 'plan',    label: 'Planner Agent' },
  { key: 'draft',   label: 'Writer Agent' },
  { key: 'review',  label: 'Reviewer Agent' },
  { key: 'approve', label: 'Human review' },
];

// ── Component ─────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState<AppView>('form');
  const [formData, setFormData] = useState<FormData>({
    pageType: 'blog_post',
    audience: 'developers',
    brand: 'brand_a',
    channel: 'web',
    notes: '',
  });
  const [wf, setWf] = useState<ActiveWorkflow | null>(null);
  const [feedback, setFeedback] = useState('');
  const [busy, setBusy] = useState(false);

  // ── Submit: auto-advance through all AI stages to HUMAN_REVIEW ────────────

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    setBusy(true);
    setWf({ id: '', phase: 'running', step: 'create' });

    const req = {
      page_type: formData.pageType,
      audience: formData.audience,
      brand: formData.brand,
      channel: formData.channel,
      notes: formData.notes || undefined,
    };

    try {
      const s1 = await createWorkflow(req);
      const id = s1.workflow_id;

      setWf({ id, phase: 'running', step: 'plan' });
      await transitionWorkflow(id, 'PLANNING');

      setWf({ id, phase: 'running', step: 'draft' });
      await transitionWorkflow(id, 'DRAFTING');

      setWf({ id, phase: 'running', step: 'review' });
      await transitionWorkflow(id, 'REVIEW');

      setWf({ id, phase: 'running', step: 'approve' });
      const final = await transitionWorkflow(id, 'HUMAN_REVIEW');

      setWf({ id, phase: 'human_review', step: 'approve', status: final });
    } catch (err) {
      setWf(prev =>
        prev ? { ...prev, phase: 'failed', error: String(err) } : null
      );
    } finally {
      setBusy(false);
    }
  }

  // ── Human review actions ───────────────────────────────────────────────────

  async function handleApprove() {
    if (!wf) return;
    setBusy(true);
    try {
      const result = await submitHumanReview(wf.id, true);
      setWf({ ...wf, phase: 'completed', status: result });
    } catch (err) {
      setWf({ ...wf, phase: 'failed', error: String(err) });
    } finally {
      setBusy(false);
    }
  }

  async function handleReject() {
    if (!wf) return;
    setBusy(true);
    try {
      await submitHumanReview(wf.id, false, feedback);
      setWf(null);
      setFeedback('');
    } catch (err) {
      setWf({ ...wf, phase: 'failed', error: String(err) });
    } finally {
      setBusy(false);
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  const draftContent =
    (wf?.status?.metadata?.review_output as string) ||
    (wf?.status?.metadata?.drafting_output as string) ||
    wf?.status?.agent_output ||
    '';

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="container">
      <header>
        <PageSection title="AI DesignOps Copilot">
          <p>Governed content generation with human approval</p>
        </PageSection>
        <nav className="tab-nav">
          <button onClick={() => setView('form')} className={view === 'form' ? 'active' : ''}>
            Request form
          </button>
          <button onClick={() => setView('tokens')} className={view === 'tokens' ? 'active' : ''}>
            Token comparison
          </button>
        </nav>
      </header>

      {view === 'tokens' ? (
        <DsComparison />
      ) : (
        <main>

          {/* ── Input form ────────────────────────────────────────────────── */}
          <Card title="New Page Request">
            <Alert type="info">
              Fill out the form and click Generate. The AI pipeline will plan, draft,
              and review content before presenting it for your approval.
            </Alert>
            <form onSubmit={handleSubmit} className="request-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Page Type</label>
                  <select
                    value={formData.pageType}
                    onChange={e => setFormData({ ...formData, pageType: e.target.value })}
                    disabled={busy}
                  >
                    <option value="landing_page">Landing Page</option>
                    <option value="product_page">Product Page</option>
                    <option value="blog_post">Blog Post</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Target Audience</label>
                  <select
                    value={formData.audience}
                    onChange={e => setFormData({ ...formData, audience: e.target.value })}
                    disabled={busy}
                  >
                    <option value="developers">Developers</option>
                    <option value="designers">Designers</option>
                    <option value="marketers">Marketers</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Brand</label>
                  <select
                    value={formData.brand}
                    onChange={e => setFormData({ ...formData, brand: e.target.value })}
                    disabled={busy}
                  >
                    <option value="brand_a">Brand A (Corporate)</option>
                    <option value="brand_b">Brand B (Modern / Tech)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Channel</label>
                  <select
                    value={formData.channel}
                    onChange={e => setFormData({ ...formData, channel: e.target.value })}
                    disabled={busy}
                  >
                    <option value="web">Web</option>
                    <option value="mobile">Mobile</option>
                    <option value="email">Email</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Additional Notes</label>
                <textarea
                  placeholder="Topic, tone, specific requirements..."
                  value={formData.notes}
                  onChange={e => setFormData({ ...formData, notes: e.target.value })}
                  disabled={busy}
                />
              </div>

              <Button type="submit" disabled={busy}>
                {busy ? 'Running pipeline...' : 'Generate Content'}
              </Button>
            </form>
          </Card>

          {/* ── Pipeline progress ─────────────────────────────────────────── */}
          {wf?.phase === 'running' && (
            <Card title="Pipeline running">
              <div className="step-list">
                {STEPS.map(s => {
                  const keys = STEPS.map(x => x.key);
                  const activeIdx = keys.indexOf(wf.step);
                  const thisIdx = keys.indexOf(s.key);
                  const done   = thisIdx < activeIdx;
                  const active = thisIdx === activeIdx;
                  return (
                    <div key={s.key} className={`step-item${done ? ' done' : ''}${active ? ' active' : ''}`}>
                      <span className="step-dot">{done ? '✓' : active ? '◉' : '○'}</span>
                      <span className="step-label">{s.label}</span>
                      {active && <span className="step-spinner">running...</span>}
                    </div>
                  );
                })}
              </div>
              <p className="step-note">Each AI stage calls the LLM — allow 10–30 s per step.</p>
            </Card>
          )}

          {/* ── Human review ──────────────────────────────────────────────── */}
          {wf?.phase === 'human_review' && (
            <Card title="Human review required">
              <Alert type="info">
                All AI stages are complete. Review the generated content and approve or reject it.
              </Alert>

              {draftContent ? (
                <div className="draft-content">
                  <p className="draft-label">Generated content</p>
                  <pre className="draft-body">{draftContent}</pre>
                </div>
              ) : (
                <p className="muted">
                  No agent output found — check <code>/workflows/{wf.id}</code> for full metadata.
                </p>
              )}

              <div className="review-actions">
                <div className="form-group">
                  <label>Rejection feedback (required to reject)</label>
                  <textarea
                    placeholder="What should the AI change or improve?"
                    value={feedback}
                    onChange={e => setFeedback(e.target.value)}
                    disabled={busy}
                  />
                </div>
                <div className="action-row">
                  <button
                    className="btn-reject"
                    onClick={handleReject}
                    disabled={busy || !feedback.trim()}
                  >
                    {busy ? '...' : 'Reject — revise'}
                  </button>
                  <Button onClick={handleApprove} disabled={busy}>
                    {busy ? 'Approving...' : 'Approve & complete'}
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* ── Completed ─────────────────────────────────────────────────── */}
          {wf?.phase === 'completed' && (
            <Card title="Content approved">
              <Alert type="info">
                Workflow <code>{wf.id.slice(0, 8)}…</code> completed successfully.
              </Alert>
              {draftContent && (
                <div className="draft-content">
                  <pre className="draft-body">{draftContent}</pre>
                </div>
              )}
              <div style={{ marginTop: 16 }}>
                <Button onClick={() => { setWf(null); setFeedback(''); }}>
                  Start new request
                </Button>
              </div>
            </Card>
          )}

          {/* ── Failed ────────────────────────────────────────────────────── */}
          {wf?.phase === 'failed' && (
            <Card title="Pipeline failed">
              <Alert type="error">{wf.error ?? 'An unexpected error occurred.'}</Alert>
              <div style={{ marginTop: 16 }}>
                <Button onClick={() => { setWf(null); setFeedback(''); }}>
                  Try again
                </Button>
              </div>
            </Card>
          )}

        </main>
      )}
    </div>
  );
}
