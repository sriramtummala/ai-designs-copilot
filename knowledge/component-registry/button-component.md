# Button Component Specification
 
## Overview
 
The Button component is used to trigger an action or event, such as submitting a form, opening a dialog, or performing a navigation.
 
## Variants
 
*   **Primary:** For the most important action on a page. (e.g., `variant="primary"`)
*   **Secondary:** For less prominent actions. (e.g., `variant="secondary"`)
*   **Tertiary (Link):** For text-based actions that navigate. (e.g., `variant="tertiary"`)
 
## States
 
*   **Default:** Standard interactive state.
*   **Hover:** Visual feedback when hovered.
*   **Focus:** Visual feedback when focused (keyboard navigation).
*   **Active:** Visual feedback when pressed.
*   **Disabled:** Non-interactive state. (e.g., `disabled={true}`)
 
## Accessibility
 
*   Must have a clear, descriptive `aria-label` if the button text is not self-explanatory (e.g., an icon-only button).
*   Must be keyboard navigable.
*   Focus indicator must be visible.
 
## Usage Examples
 
```jsx
<Button variant="primary" onClick={handleSubmit}>Submit</Button>
<Button variant="secondary" disabled>Cancel</Button>
