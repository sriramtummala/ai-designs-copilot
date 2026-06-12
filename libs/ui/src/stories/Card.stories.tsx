import type { Meta, StoryObj } from '@storybook/react-vite';
import { Card } from '../Card';

const meta = {
  title: 'UI/Card',
  component: Card,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      control: 'text',
    },
  },
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'Card Title',
    children: <p>This is the content of the card. It can hold any React elements.</p>,
  },
};

export const NoTitle: Story = {
  args: {
    children: <p>This card has no title.</p>,
  },
};
