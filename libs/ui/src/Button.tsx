import React from 'react';

export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary';
  type?: 'button' | 'submit' | 'reset';
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ children, onClick, variant = 'primary', type = 'button', disabled = false }) => {
  const buttonStyle: React.CSSProperties = {
    padding: `var(--spacing-md) var(--spacing-lg)`,
    borderRadius: `var(--radius-sm)`,
    border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: `var(--font-weight-bold)`,
    fontSize: `var(--font-size-md)`,
    opacity: disabled ? 0.5 : 1,
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
    <button style={buttonStyle} onClick={onClick} type={type} disabled={disabled}>
      {children}
    </button>
  );
};
 
export { Button };
