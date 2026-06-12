import type { Meta, StoryObj } from '@storybook/react-vite';
import { Alert } from '../Alert';

const meta = {
  title: 'UI/Alert',
  component: Alert,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    type: {
      control: 'select',
      options: ['info', 'warning', 'error'],
    },
  },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Info: Story = {
  args: {
    type: 'info',
    children: 'This is an informational alert message.',
  },
};

export const Warning: Story = {
  args: {
    type: 'warning',
    children: 'Warning: Something might be wrong here.',
  },
};

export const Error: Story = {
  args: {
    type: 'error',
    children: 'Error: Action failed. Please try again.',
  },
};
