import { useState } from 'react'
import './App.css'

interface PageRequest {
  pageType: string
  audience: string
  brand: string
  channel: string
  campaignNotes: string
  constraints: string
}

const EMPTY: PageRequest = {
  pageType: '',
  audience: '',
  brand: '',
  channel: '',
  campaignNotes: '',
  constraints: '',
}

function App() {
  const [form, setForm] = useState<PageRequest>(EMPTY)
  const [submitted, setSubmitted] = useState(false)

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setSubmitted(true)
  }

  function handleReset() {
    setForm(EMPTY)
    setSubmitted(false)
  }

  return (
    <main className="container">
      <header>
        <h1>AI DesignOps Copilot</h1>
        <p className="subtitle">Governed page-generation workflow</p>
      </header>

      {submitted ? (
        <section className="card">
          <h2>Request received</h2>
          <pre className="output">{JSON.stringify(form, null, 2)}</pre>
          <p className="note">Workflow orchestration is not yet wired. This output confirms the intake form is working.</p>
          <button onClick={handleReset}>Start over</button>
        </section>
      ) : (
        <form className="card" onSubmit={handleSubmit}>
          <h2>New page request</h2>

          <label>
            Page type
            <select name="pageType" value={form.pageType} onChange={handleChange} required>
              <option value="">Select…</option>
              <option value="campaign-landing">Campaign landing</option>
              <option value="product-detail">Product detail</option>
              <option value="category-hub">Category hub</option>
              <option value="editorial">Editorial</option>
            </select>
          </label>

          <label>
            Audience
            <input name="audience" value={form.audience} onChange={handleChange} placeholder="e.g. loyalty members, new visitors" required />
          </label>

          <label>
            Brand
            <input name="brand" value={form.brand} onChange={handleChange} placeholder="e.g. QuikTrip, sub-brand name" required />
          </label>

          <label>
            Channel
            <select name="channel" value={form.channel} onChange={handleChange} required>
              <option value="">Select…</option>
              <option value="web">Web</option>
              <option value="mobile-web">Mobile web</option>
              <option value="app">App</option>
              <option value="email">Email</option>
            </select>
          </label>

          <label>
            Campaign notes
            <textarea name="campaignNotes" value={form.campaignNotes} onChange={handleChange} rows={3} placeholder="Describe the campaign goal or content brief" />
          </label>

          <label>
            Constraints
            <textarea name="constraints" value={form.constraints} onChange={handleChange} rows={2} placeholder="e.g. must use DS 2.0 components, no hero images" />
          </label>

          <button type="submit">Submit request</button>
        </form>
      )}
    </main>
  )
}

export default App
