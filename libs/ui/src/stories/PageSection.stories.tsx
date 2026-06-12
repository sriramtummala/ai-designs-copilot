import type { Meta, StoryObj } from '@storybook/react-vite';
import { PageSection } from '../PageSection';

const meta = {
  title: 'UI/PageSection',
  component: PageSection,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
    },
  },
} satisfies Meta<typeof PageSection>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'Welcome to the Section',
    children: (
      <div style={{ padding: '20px' }}>
        <p>This is some content within the page section.</p>
        <p>It helps organize content on a page.</p>
      </div>
    ),
  },
};

export const NoTitle: Story = {
  args: {
    children: (
      <div style={{ padding: '20px' }}>
        <p>This section has no title.</p>
      </div>
    ),
  },
};
