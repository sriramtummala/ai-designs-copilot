import React from 'react';
 
interface CardProps {
  children: React.ReactNode;
  title?: string;
}
 
const Card: React.FC<CardProps> = ({ children, title }) => {
  const cardStyle: React.CSSProperties = {
    backgroundColor: `var(--color-background-default)`,
    borderRadius: `var(--radius-md)`,
    boxShadow: `var(--elevation-1)`,
    padding: `var(--spacing-lg)`,
    margin: `var(--spacing-md) 0`,
  };
 
  const titleStyle: React.CSSProperties = {
    fontSize: `var(--font-size-xl)`,
    fontWeight: `var(--font-weight-bold)`,
    color: `var(--color-text-default)`,
    marginBottom: `var(--spacing-md)`,
  };
 
  return (
    <div style={cardStyle}>
      {title && <h2 style={titleStyle}>{title}</h2>}
      {children}
    </div>
  );
};
 
export { Card };
