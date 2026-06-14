```markdown
# Alert Component Specification
 
## Overview
 
The Alert component provides a concise and informative message to the user, often in response to an action or system event.
 
## Types
 
*   **Info:** For general information. (e.g., `type="info"`)
*   **Success:** For successful operations. (e.g., `type="success"`)
*   **Warning:** For potential issues or non-critical errors. (e.g., `type="warning"`)
*   **Error:** For critical errors that require user attention. (e.g., `type="error"`)
 
## Accessibility
 
*   Use `aria-live="polite"` for non-critical alerts that don't immediately demand user attention.
*   Use `aria-live="assertive"` for critical alerts that require immediate user attention.
*   Ensure the message is clear and actionable.
 
## Usage Examples
 
```jsx
<Alert type="info">Your settings have been saved.</Alert>
<Alert type="error">Failed to load data. Please refresh the page.</Alert>
