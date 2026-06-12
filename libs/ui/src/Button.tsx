import React from 'react';

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  type?: 'button' | 'submit' | 'reset';
}
 
const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary', type = 'button' }) => {
  const buttonStyle: React.CSSProperties = {
    padding: `var(--spacing-md) var(--spacing-lg)`,
    borderRadius: `var(--radius-sm)`,
    border: 'none',
    cursor: 'pointer',
    fontWeight: `var(--font-weight-bold)`,
    fontSize: `var(--font-size-md)`,
  };
 
  if (variant === 'primary') {
    buttonStyle.backgroundColor = `var(--color-brand-primary)`;
    buttonStyle.color = `var(--color-text-inverse)`;
  } else if (variant === 'secondary') {
    buttonStyle.backgroundColor = `var(--color-background-alt)`;
    buttonStyle.color = `var(--color-text-default)`;
    buttonStyle.border = `1px solid var(--color-gray-300)`;
  }
 
  return (
    <button style={buttonStyle} onClick={onClick} type={type}>
      {children}
    </button>
  );
};
 
export { Button };
