import React from 'react';
 
export interface PageSectionProps {
  children: React.ReactNode;
  title?: string;
}
 
const PageSection: React.FC<PageSectionProps> = ({ children, title }) => {
  const sectionStyle: React.CSSProperties = {
    padding: `var(--spacing-xl) 0`,
    borderBottom: `1px solid var(--color-gray-200)`,
    marginBottom: `var(--spacing-xl)`,
  };
 
  const titleStyle: React.CSSProperties = {
    fontSize: `var(--font-size-xl)`,
    fontWeight: `var(--font-weight-bold)`,
    color: `var(--color-text-default)`,
    marginBottom: `var(--spacing-lg)`,
  };
 
  return (
    <section style={sectionStyle}>
      {title && <h2 style={titleStyle}>{title}</h2>}
      {children}
    </section>
  );
};
 
export { PageSection };