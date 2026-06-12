import path from 'path';
import { fileURLToPath } from 'url';
import type { StorybookConfig } from '@storybook/react-vite';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

const config: StorybookConfig = {
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  viteFinal(viteConfig) {
    viteConfig.resolve ??= {};
    viteConfig.resolve.alias = {
      ...(viteConfig.resolve.alias as Record<string, string>),
      '@ai-designops/tokens/theme.css': path.resolve(__dirname, '../../tokens/dist/css/theme.css'),
      '@ai-designops/tokens': path.resolve(__dirname, '../../tokens/dist/js'),
    };
    return viteConfig;
  },
};

export default config;
