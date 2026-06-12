import { Button, Card, Alert } from '@ai-designops/ui'

const DS2_OVERRIDES: Record<string, string> = {
  '--color-brand-primary': '#1d4ed8',
  '--color-brand-secondary': '#22c55e',
  '--color-text-default': '#1f2937',
  '--color-text-light': '#6b7280',
  '--color-background-alt': '#f9fafb',
  '--spacing-xs': '6px',
  '--spacing-sm': '10px',
  '--spacing-md': '18px',
  '--spacing-lg': '28px',
  '--spacing-xl': '36px',
  '--elevation-1': '0px 2px 4px rgba(0, 0, 0, 0.15)',
  '--elevation-2': '0px 6px 10px rgba(0, 0, 0, 0.15)',
}

const DS1_VALUES: Record<string, string> = {
  '--color-brand-primary': '#3b82f6',
  '--color-brand-secondary': '#8b5cf6',
  '--color-text-default': '#111827',
  '--color-text-light': '#4b5563',
  '--color-background-alt': '#f3f4f6',
  '--spacing-xs': '4px',
  '--spacing-sm': '8px',
  '--spacing-md': '16px',
  '--spacing-lg': '24px',
  '--spacing-xl': '32px',
  '--elevation-1': '0px 1px 3px rgba(0,0,0,0.1)',
  '--elevation-2': '0px 4px 6px rgba(0,0,0,0.1)',
}

function TokenSwatch({ value }: { value: string }) {
  const isColor = value.startsWith('#') || value.startsWith('rgb')
  if (!isColor) return <code style={{ fontSize: 12 }}>{value}</code>
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
      <span style={{
        display: 'inline-block',
        width: 16,
        height: 16,
        borderRadius: 3,
        background: value,
        border: '1px solid #d1d5db',
        flexShrink: 0,
      }} />
      <code style={{ fontSize: 12 }}>{value}</code>
    </span>
  )
}

function ComponentPreview({ scoped }: { scoped?: boolean }) {
  const overrides = scoped
    ? Object.fromEntries(Object.entries(DS2_OVERRIDES).map(([k, v]) => [k, v])) as React.CSSProperties
    : {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, ...overrides }}>
      <Button variant="primary">Primary button</Button>
      <Button variant="secondary">Secondary button</Button>
      <Alert type="info">Info alert with brand colors</Alert>
      <Card title="Sample card">Card body text using design tokens.</Card>
    </div>
  )
}

export default function DsComparison() {
  return (
    <div style={{ padding: '24px 20px', maxWidth: 1100, margin: '0 auto' }}>
      <h1 style={{ marginBottom: 4 }}>Token Comparison</h1>
      <p style={{ color: 'var(--color-text-light)', marginBottom: 32 }}>
        DS 1.0 vs DS 2.0 — visual diff of brand refresh
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 40 }}>
        <div>
          <h2 style={{ marginBottom: 16, fontSize: 16 }}>DS 1.0</h2>
          <ComponentPreview />
        </div>
        <div>
          <h2 style={{ marginBottom: 16, fontSize: 16 }}>DS 2.0</h2>
          <ComponentPreview scoped />
        </div>
      </div>

      <h2 style={{ marginBottom: 12, fontSize: 16 }}>Changed tokens</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr style={{ background: 'var(--color-background-alt)', textAlign: 'left' }}>
            <th style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)' }}>Token</th>
            <th style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)' }}>DS 1.0</th>
            <th style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)' }}>DS 2.0</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(DS2_OVERRIDES).map(([token, v2]) => (
            <tr key={token}>
              <td style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)', fontFamily: 'monospace' }}>{token}</td>
              <td style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)' }}>
                <TokenSwatch value={DS1_VALUES[token]} />
              </td>
              <td style={{ padding: '8px 12px', border: '1px solid var(--color-gray-200)' }}>
                <TokenSwatch value={v2} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
