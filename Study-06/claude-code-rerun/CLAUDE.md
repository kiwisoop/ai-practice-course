# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Shopping List App** — A simple, single-file web application for managing shopping lists. Users can add items, mark them as complete, delete items, and see completion statistics. Data persists using browser localStorage.

**Technology Stack:**
- Pure vanilla JavaScript (no frameworks or build tools)
- HTML5 semantic markup
- CSS3 with Flexbox layout
- Browser localStorage for data persistence
- Korean language interface

**Project Structure:**
- `shopping-list.html` — Single-file application containing all HTML, CSS, and JavaScript

## Running the App Locally

Open `shopping-list.html` directly in a web browser:
```bash
open shopping-list.html
# or on Windows/Linux:
# firefox shopping-list.html
```

The app runs entirely in the browser with no server or build step required. Data is stored in localStorage, so it persists across browser sessions.

## Application Architecture

### Data Model
Shopping items are stored as an array of objects in localStorage:
```javascript
[
  { text: "소금", completed: false },
  { text: "우유", completed: true }
]
```

### Core Functions
- **loadItems()** — Retrieves items from localStorage; returns empty array if no data exists
- **saveItems(items)** — Persists items array to localStorage
- **renderItems()** — Renders the full item list from DOM, handling empty state
- **addItem()** — Creates a new item from input, saves, and refreshes UI
- **deleteItem(index)** — Removes item at index, saves, and refreshes UI
- **toggleItem(index)** — Toggles completed status, saves, and refreshes UI
- **updateStats()** — Recalculates and displays total and completed counts

### UI State
The DOM is rebuilt on every state change via `renderItems()`. This is simple but means changes ripple through the entire list. For this small-scale app, this is appropriate and keeps the code readable.

## Development Notes

### Styling
- Uses CSS gradient background (`#667eea` to `#764ba2`)
- Responsive design: max-width 500px container, padding adjusts on small screens
- Hover states and transitions for interactive feedback
- Completed items show visual feedback (strikethrough, reduced opacity)

### Language & Localization
The interface is fully in Korean (한국어). All user-facing text uses Korean strings. When adding features or modifying UI text, maintain Korean language throughout.

### Storage Key
Items are stored under the key `'shoppingList'` in localStorage. Do not change this key without migration logic.

### Event Handling
- **Button click** — Triggers `addItem()`
- **Enter key** in input — Triggers `addItem()`
- **Checkbox change** — Toggles item completion
- **Delete button click** — Removes item

### Browser Compatibility
The app uses standard ES6 JavaScript and CSS features supported in all modern browsers. No polyfills required.
