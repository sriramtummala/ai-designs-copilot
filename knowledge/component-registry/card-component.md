
```markdown
# Card Component Specification
 
## Overview
 
The Card component is a flexible and extensible content container. It groups related content and actions together, making information easier to digest.
 
## Structure
 
*   **Header (Optional):** Contains a title, subtitle, or avatar.
*   **Media (Optional):** Image or video.
*   **Content:** Main text or rich media.
*   **Actions (Optional):** Buttons or links related to the card content.
 
## Variants
 
*   **Default:** Standard card with shadow.
*   **Flat:** Card with no shadow, often used in lists.
 
## Accessibility
 
*   Ensure proper heading structure within the card content.
*   If the entire card is clickable, use a single interactive element (e.g., a link wrapping the card content) rather than multiple nested interactive elements.
 
## Usage Examples
 
```jsx
<Card title="Product Update">
  <p>New features are now available!</p>
  <Button>Learn More</Button>
</Card>
