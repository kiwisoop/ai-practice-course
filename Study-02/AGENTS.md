# Kiwibird Project Instructions

## Project Overview

Kiwibird is a personal task manager for the fourth-week AI practice assignment. It runs directly in a browser and uses a friendly green-and-cream kiwi-bird theme. Read `PRD.md` for the agreed requirements and `PROMPTS.md` for the five implementation stages.

## Working Process

- Implement one step from `PROMPTS.md` at a time.
- Preserve every verified feature from earlier steps.
- Do not implement later-step features early.
- After each step, run the listed checks and report the results.
- Keep each step as a separate Git commit using the suggested message.
- Update documentation when the implemented behavior changes.

## Technology

- Use only HTML, CSS, and vanilla JavaScript.
- Do not add frameworks, package managers, build tools, external APIs, or remotely hosted images. Keep visual assets in the local `assets` folder.
- The app must work by opening `index.html` directly in a current browser.
- Prefer native browser features such as `input type="date"`, `localStorage`, file inputs, and Blob downloads.

## Planned Files

```text
Study-02/
├── assets/
├── AGENTS.md
├── PRD.md
├── PROMPTS.md
├── README.md
├── index.html
├── styles.css
└── script.js
```

Create only the files needed by the current stage. `README.md` is completed in Step 5.

## Code Style

- Write filenames, HTML attributes, JavaScript identifiers, and code comments in English.
- Write user-facing text in natural Korean.
- Keep functions small and named for one clear responsibility.
- Reuse existing rendering, filtering, and state-update paths instead of duplicating logic.
- Prefer readable conditions and browser APIs over custom abstractions.
- Keep application state in one obvious place and update the UI through shared render functions.

## Data and Safety

- Trim task titles and reject empty input.
- Render user text safely; never inject it as HTML.
- Confirm destructive actions before changing data.
- Validate imported JSON completely before replacing current tasks.
- Leave current data unchanged when import validation fails or the user cancels.
- Accept focus durations only as integers from 5 to 120 minutes.
- Never store or transmit credentials, API keys, or sensitive personal data.

## Accessibility

- Associate inputs with visible labels or accessible names.
- Support keyboard operation and visible focus styles.
- Do not communicate category, priority, status, or errors by color alone.
- Announce important status and validation messages in the page.
- Keep controls large enough to use on mobile screens.
- Show timer state and remaining time as text.

## Verification

- Follow the direct checks listed under the current step in `PROMPTS.md`.
- Check the browser console for errors after meaningful changes.
- Check both desktop and mobile-width layouts.
- Verify boundary cases for dates, empty lists, filters, focus time, and JSON import.
- Do not add a test framework unless the existing browser checks cannot verify non-trivial logic reliably.

## Scope Boundaries

Do not add login, cloud synchronization, collaboration, push notifications, recurring tasks, custom categories, analytics, or an external quote service. Ask before expanding beyond `PRD.md`.
