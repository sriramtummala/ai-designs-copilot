import React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import tokens from '../../../tokens/dist/json/tokens-docs.json';

const meta = {
  title: 'Design System/Tokens',
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

const TokenDisplay = () => {
  const renderTokens = (obj: Record<string, unknown>, path: string[] = []) => {
    return Object.entries(obj).map(([key, value]) => {
      const currentPath = [...path, key];
      const tokenName = currentPath.join('.');

      if (typeof value === 'object' && value !== null && !('value' in value)) {
        return (
          <div key={tokenName} style={{ marginLeft: '20px' }}>
            <h3>{key}</h3>
            {renderTokens(value as Record<string, unknown>, currentPath)}
          </div>
        );
      }

      if (typeof value === 'object' && value !== null && 'value' in value) {
        const tokenValue = (value as { value: string }).value;
        const cssVar = `--${tokenName.replace(/\./g, '-')}`;

        let stylePreview: React.CSSProperties = {};
        let previewLabel = '';

        if (tokenName.startsWith('color')) {
          stylePreview = { backgroundColor: tokenValue, width: 30, height: 30, borderRadius: 4, border: '1px solid #ccc' };
        } else if (tokenName.startsWith('spacing')) {
          stylePreview = { width: tokenValue, height: 10, backgroundColor: 'var(--color-blue-500)' };
        } else if (tokenName.startsWith('font.size')) {
          stylePreview = { fontSize: tokenValue };
          previewLabel = 'Aa';
        }

        return (
          <div key={tokenName} style={{ display: 'flex', alignItems: 'center', marginBottom: 10, borderBottom: '1px solid #eee', paddingBottom: 5 }}>
            <div style={{ minWidth: 200, fontWeight: 'bold' }}>{tokenName}</div>
            <div style={{ minWidth: 150 }}>{tokenValue}</div>
            <div style={{ minWidth: 150, color: '#888', fontSize: 12 }}>{cssVar}</div>
            <div style={{ ...stylePreview, marginLeft: 10 }}>{previewLabel}</div>
          </div>
        );
      }

      return null;
    });
  };

  return (
    <div style={{ fontFamily: 'var(--font-family-base)', padding: 20 }}>
      <h1>Design Tokens</h1>
      <p>All design tokens defined in the system, with their values and corresponding CSS variables.</p>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 10, borderBottom: '2px solid #333', paddingBottom: 5, marginTop: 20 }}>
        <div style={{ minWidth: 200, fontWeight: 'bold' }}>Token Name</div>
        <div style={{ minWidth: 150, fontWeight: 'bold' }}>Value</div>
        <div style={{ minWidth: 150, fontWeight: 'bold' }}>CSS Variable</div>
        <div style={{ marginLeft: 10, fontWeight: 'bold' }}>Preview</div>
      </div>
      {renderTokens(tokens as Record<string, unknown>)}
    </div>
  );
};

export const AllTokens: Story = {
  render: () => <TokenDisplay />,
};
