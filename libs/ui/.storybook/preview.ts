/// <reference path="../src/global.d.ts" />
import '../../tokens/dist/css/theme.css';
import type { Preview } from '@storybook/react-vite';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /date/i,
      },
    },
  },
};

export default preview;
