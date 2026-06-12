# Design Tokens Library
 
This library serves as the single source of truth for all design tokens used across the AI DesignOps Copilot. Design tokens are the visual design atoms of our system – specifically named entities that store visual design attributes.
 
## Structure
 
Tokens are organized into `source` directories, typically versioned (e.g., `ds-1.0`, `ds-2.0`). Within each version, `tokens.json` defines the token set.
 
## Primitive vs. Semantic Tokens
 
*   **Primitive Tokens:** These are raw, atomic values (e.g., specific hex codes for colors, pixel values for spacing). They are the lowest level of abstraction and do not carry any contextual meaning.
    *   *Example:* `color.blue.500: #3b82f6`
 
*   **Semantic Tokens:** These are context-aware aliases that refer to primitive tokens. They provide meaning and flexibility, allowing for easy theming and adaptation to different contexts (e.g., dark mode, different brands).
    *   *Example:* `color.brand.primary: {color.blue.500}`
 
This separation ensures that changes to raw values (primitives) can be managed centrally, while their application (semantics) can be updated consistently across the entire design system.
 
## Usage
 
These tokens will be transformed into platform-specific formats (CSS variables, TypeScript objects) using Style Dictionary, which will then be consumed by UI components in `libs/ui` and applications like `apps/web`.
