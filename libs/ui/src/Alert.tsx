import React from 'react';
 
export interface AlertProps {
  children: React.ReactNode;
  type?: 'info' | 'warning' | 'error';
}
 
const Alert: React.FC<AlertProps> = ({ children, type = 'info' }) => {
  const alertStyle: React.CSSProperties = {
    padding: `var(--spacing-md)`,
    borderRadius: `var(--radius-sm)`,
    marginBottom: `var(--spacing-md)`,
    fontSize: `var(--font-size-sm)`,
    color: `var(--color-text-inverse)`,
  };
 
  if (type === 'info') {
    alertStyle.backgroundColor = `var(--color-blue-600)`;
  } else if (type === 'warning') {
    alertStyle.backgroundColor = `var(--color-purple-600)`; // Using purple as a placeholder for warning
  } else if (type === 'error') {
    alertStyle.backgroundColor = `var(--color-gray-700)`; // Using gray as a placeholder for error
  }
 
  return (
    <div style={alertStyle}>
      {children}
    </div>
  );
};
 
export { Alert };
