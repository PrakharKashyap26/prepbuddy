# PrepBuddy Frontend Layout & UX Audit

This audit log records the UI, UX, and layout concerns diagnosed across the PrepBuddy v1.0 interface, alongside the responsive modifications applied.

---

## 🔍 UI & UX Concerns Found

### 1. Viewport Heights & Page Scroll Wars
- **Symptom**: Chat conversations with many messages pushed the Socratic input box and the page header upwards, scrolling them completely off-screen.
- **Cause**: The main outer viewport did not lock body scroll, and heights inside the chat box were not bounded.
- **Fix**: Wrapped main page contents inside `.app-viewport` and `.viewport-body` containers. Set `html, body { height: 100vh; overflow: hidden; }` to lock page-level scrolls. Forced the Chat page to use `.chat-workspace { height: 100%; overflow: hidden; }` and restricted scroll strictly to `.chat-scroll`.

### 2. Socratic Chat Input & Tag Shifts
- **Symptom**: Long chats or typing inputs caused visual shifts, overlapping message cards, or breaking bounds on zoom configurations (100% down to 67%).
- **Fix**: Anchored the send container at the bottom using `flex-shrink: 0;` inside the flex columns container. Configured `.socratic-prompts-row` to use flex layouts that horizontal-scroll naturally on mobile screens.

### 3. Screen Width Squishing & Sidebars
- **Symptom**: At widths under 768px (tablets and mobiles), the left-hand navigation sidebar compressed columns, shrinking content areas and rendering buttons unusable.
- **Fix**: Implemented media queries to hide the sidebar `.app-sidebar` on screens under `768px` and display a custom `.mobile-bottom-nav` bar anchored fixed to the bottom of the screen.

### 4. Text & Code Snippet Wrapping
- **Symptom**: Long URL strings inside Course cards and raw code syntax blocks inside chatbot answers broke card containers, generating horizontal scrolling bars.
- **Fix**: Applied `word-break: break-all;` to course links and `word-break: break-word; white-space: pre-wrap;` to chat message bubbles. Integrated a regex-based Markdown formatter inside `chat.js` to wrap codes within `<pre><code>` structures.

---

## 🛠️ Summary of Stylesheets Standardizations
- **[global.css](file:///c:/projects_&_coding/prepbuddy/frontend/css/global.css)**: Holds all layout grids, typography configurations, button variations, and mobile bottom tab designs.
- **[auth.css](file:///c:/projects_&_coding/prepbuddy/frontend/css/auth.css)**: Implements mobile padding adjustments for centered forms.
- **[dashboard.css](file:///c:/projects_&_coding/prepbuddy/frontend/css/dashboard.css)**: Handles stats wrapping and table scrolls.
- **[chat.css](file:///c:/projects_&_coding/prepbuddy/frontend/css/chat.css)**: Coordinates absolute heights for independent chat scrolls and code block formats.
- **[courses.css](file:///c:/projects_&_coding/prepbuddy/frontend/css/courses.css)**: Resolves search grids wrapping.
