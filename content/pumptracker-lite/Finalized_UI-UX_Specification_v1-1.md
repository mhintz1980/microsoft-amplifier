# PumpTracker Lite UI/UX Specification

## Introduction

This document defines the user experience goals, information architecture, user flows, and visual design specifications for PumpTracker Lite's user interface. It serves as the foundation for visual design and frontend development, ensuring a cohesive and user-centered experience.

### Overall UX Goals & Principles

#### Target User Personas

* **Primary User:** A manufacturing workflow manager responsible for tracking pump orders through production stages. They need a quick overview of status (Dashboard) and efficient tools for managing individual pump progression (Kanban).

#### Usability Goals

* **Efficiency:** Quickly grasp overall production status via the Dashboard KPIs and visualizations.
* **Clarity:** Easily understand pump status and bottlenecks on both the Dashboard and Kanban board.
* **Speed:** Add new Purchase Orders and associated pumps with minimal friction via the "Add PO" modal.
* **Intuitiveness:** Effortlessly move pumps between stages using drag-and-drop on the Kanban board. **Ensure required data (like serial numbers) is captured contextually**.

#### Design Principles

1.  **Clarity First:** Prioritize clear information display over complex visuals. Ensure KPIs, charts, and card data are immediately understandable.
2.  **Efficiency in Action:** Streamline core workflows like adding POs and moving pumps. Minimize clicks and required inputs.
3.  **Visual Consistency:** Maintain a cohesive aesthetic aligned with the quality standards exemplified by 21st.dev Magic, using the defined Layer Stack and Motion Recipes consistently. Components must be built using ShadCN/ui primitives, styled with Tailwind tokens, and adhere to defined constraints.
4.  **Responsive Feedback:** Provide immediate visual feedback for user actions like filtering, drag-and-drop, and modal interactions, using Framer Motion subtly according to defined recipes.
5.  **Focus on the Core:** Keep the interface clean and focused on the primary tasks of status overview and order management, deferring non-essential features.
6.  **Layered Clarity:** Employ visual depth using layers, shadows, and translucency to organize information, drawing inspiration from the Layer Stack concept in `docs/UI-Guidelines.md`.
7.  **Subtle, Purposeful Motion:** Utilize animations for feedback and hierarchy, referencing the Motion Recipes in `docs/UI-Guidelines.md` as preferred starting points for consistency.

---

### Change Log

| Date             | Version | Description                   | Author     |
| :--------------- | :------ | :---------------------------- | :--------- |
| October 23, 2025 | 1.0     | Initial draft based on PRD v2 | Sally (UX) |
| October 23, 2025 | 1.1     | Added constraints & style details | Sally (UX) |

---

## Information Architecture (IA)

### Site Map / Screen Inventory

This diagram shows the primary navigable views within the application shell. Modals (Add PO, Pump Details, PO Details, **Assign Serial**) are accessed contextually.

```mermaid
graph TD
    subgraph App Shell
        A[Dashboard (/dashboard)]
        B[Kanban Board (/kanban)]
    end

    style App Shell fill:#f0f0f0,stroke:#ccc,stroke-dasharray: 5 5
```
**Navigation Structure**

*Primary Navigation: A persistent header bar will contain simple links allowing users to switch between the Dashboard (/dashboard) and the Kanban Board (/kanban).
*Persistent Toolbar: Located below the header, this toolbar is always visible and contains the Global Filter Bar and the "Add PO" Button.
*Breadcrumb Strategy: Not applicable for this simple two-view structure.

## User Flows

### Add New Purchase Order

* **User Goal:** To add a new purchase order with multiple line items, resulting in individual pump entries being created in the system (without initial serial numbers).
* **Entry Points:** Clicking the "Add PO" button in the persistent header toolbar.
* **Success Criteria:** The Add PO modal closes, and new pump cards (using defaults from Model, serial undefined) appear in the "NOT STARTED" stage. Default pricing is applied but editable.

**Flow Diagram**
```mermaid
graph TD
    A[User Clicks "Add PO" Button] --> B{Open Add PO Modal};
    B --> C[User Fills PO Info (PO#, Cust, Dates)];
    C --> D[User Adds Line Items (Model, Qty, Color, Priority, Value, Line Date)];
    D --> E{User Clicks Submit};
    E -- Validation OK --> F[Expand Lines into Pumps (Defaults from Model, No Serial)];
    F --> G[Update App State (Zustand)];
    G --> H[Call Data Adapter Upsert (PO, Lines, Pumps)];
    H --> I[Close Modal];
    I --> J[New Pumps Appear in 'NOT STARTED'];
    E -- Validation Fail --> K[Show Error Messages in Modal];
    K --> D;

    style J fill:#90EE90
```

**Edge Cases & Error Handling:**

* Required fields validated. Show inline errors.
* Handle adapter errors.
* Closing modal discards changes.

---

### Move Pump on Kanban Board (with Serial Check)

* **User Goal:** To update the production stage of a pump, potentially being prompted to add a serial number if moving to Powder Coat.
* **Entry Points:** Dragging a pump card on the Kanban board (`/kanban`).
* **Success Criteria:** Pump visually moves, state updates, change persists, toast confirms. If moving to Powder Coat without serial, Assign Serial modal appears first; successful serial entry completes the move. Stage move creates a PumpEvent.

**Flow Diagram**
```mermaid
graph TD
    A[User Drags Pump Card] --> B{Drop on New Stage Column};
    B --> C{Target='Powder Coat' AND Serial Missing?};
    C -- Yes --> D[Open Assign Serial Modal];
    D --> E{User Enters Serial & Saves};
    E -- Valid & Unique Serial --> F[Store: assignSerialAndMoveStage];
    E -- Invalid/Duplicate Serial --> G[Show Error in Modal];
    E -- Cancel --> H[Close Modal, Card Returns];
    C -- No --> I[Store: moveStage];
    F --> J[Call Adapter: updatePump (with serial, stage, event)];
    I --> J[Call Adapter: updatePump (with stage, event)];
    J -- Success --> K[Show Success Toast];
    K --> L[Pump Visually in New Column];
    L -- If Stage='SHIPPING' --> M[Trigger KPI Recalc];
    J -- Adapter Error --> N[Rollback State];
    N --> O[Show Error Toast];
    O --> P[Card Returns];
    G --> D;

    style L fill:#90EE90
```

**Edge Cases & Error Handling:**

* Invalid drop target returns card.
* Adapter errors rollback state and show error toast.
* Serial validation (uniqueness) occurs in Assign Serial modal.

---

### Add/Edit Serial Number via Pump Details Modal

* **User Goal:** To add or correct the serial number for an existing pump.
* **Entry Points:** Double-clicking pump card/row → Open Pump Details Modal → Click Edit.
* **Success Criteria:** Serial number field is updated, uniqueness check passes, state is updated, change persists, modal returns to read-only view.

**Flow Diagram**
```mermaid
graph TD
    A[User Opens Pump Details Modal] --> B[User Clicks Edit];
    B --> C[User Enters/Modifies Serial Number];
    C --> D{User Clicks Save};
    D --> E{Validate Serial (Unique?)};
    E -- Valid & Unique --> F[Store: updatePump (with serial)];
    E -- Invalid/Duplicate --> G[Show Error in Modal];
    F --> H[Call Adapter: updatePump];
    H -- Success --> I[Return Modal to Read-Only];
    H -- Adapter Error --> J[Show Error Toast];
    G --> C;
    I --> K[Serial Updated in UI];

    style K fill:#90EE90
```

---

## Wireframes & Mockups

This section clarifies where the detailed visual designs reside and provides a conceptual layout for the key screens defined in the PRD.

* **Primary Design Files:** `[Link to Figma/Sketch/XD Project - To Be Provided]` - This will be the central location for detailed mockups, prototypes, and final visual designs.

---

### Key Screen Layouts

These are conceptual descriptions to guide the visual design process.

#### Dashboard (`/dashboard`)

* **Purpose:** Provide a high-level overview of production status, key metrics, and upcoming work.
* **Key Elements:**
    * Persistent Header & Toolbar (Navigation, Filters, Add PO button).
    * KPI Strip (Avg Build Time, On-Time %, Efficiency, Ship Count, Value).
    * Workload Donuts (Pumps by Customer, Model).
    * Build Time Trend Chart (AreaChart).
    * Capacity Radials (Weekly demand vs capacity).
    * Timeline (Gantt-lite view) - *(Note: May be removed post-MVP)*.
    * PO + Pump List Table (Expandable rows).
* **Interaction Notes:** Table rows double-clickable. Filters affect all content. Widgets animate on entry.
* **Design File Reference:** `[Link to Dashboard Frame/Artboard - TBP]`

---

#### Kanban Board (`/kanban`)

* **Purpose:** Allow users to visually track and manage pumps through production stages via drag-and-drop.
* **Key Elements:**
    * Persistent Header & Toolbar.
    * Stage Columns (`NOT STARTED` to `SHIPPING`) with headers (count, collapse toggle).
    * Pump Cards (Model, Customer, Serial/Placeholder, PO, Priority indicator). Expanded/Collapsed states.
* **Interaction Notes:** Draggable cards (`@dnd-kit`). Drag to Powder Coat triggers serial check/modal if needed. Double-click card opens Pump Details Modal. Column collapse toggle.
* **Design File Reference:** `[Link to Kanban Frame/Artboard - TBP]`

---

#### Add PO Modal

* **Purpose:** Input new Purchase Order and line items.
* **Key Elements:**
    * Modal Title. PO-level fields (PO #, Cust, Dates).
    * Dynamic Line Items section (Model, Qty, Color, Priority, Value (editable default), Line Date).
    * "Add/Remove Line" buttons. Footer ("Submit", "Cancel").
* **Interaction Notes:** Value auto-populates from Model entity. Validation on submit. No serial input here.
* **Design File Reference:** `[Link to Add PO Modal Frame/Artboard - TBP]`

---

#### Pump Details Modal

* **Purpose:** Display and edit details for a single pump.
* **Key Elements:**
    * Modal Title. Read-only fields initially.
    * Editable field for Serial Number (optional).
    * Fields for all other `Pump` properties (PO, Model, Stage, Priority, Color, Value, Build Time, Dates, etc.). Viewable BOM section.
    * Footer ("Edit", "Save", "Cancel", "Close").
* **Interaction Notes:** "Edit" enables fields. "Save" validates (including serial uniqueness), persists changes, returns to read-only. Accessed via double-click.
* **Design File Reference:** `[Link to Pump Details Modal Frame/Artboard - TBP]`

---

#### Purchase Order Details Modal

* **Purpose:** Display PO info, associated lines, and pumps. Allow editing PO/Line details.
* **Key Elements:**
    * Modal Title. PO fields (Cust, Dates, Notes).
    * Normalized Line Items section (Model, Qty, Priority, Color, Value Each, Line Promise Date).
    * List/table of associated Pumps. Pricing summary.
    * Read-only initially. Footer ("Edit", "Save", "Cancel", "Close").
* **Interaction Notes:** "Edit" enables PO/Line fields. Saving persists updates, potentially prompts to cascade value changes to Pumps. Accessed via double-click on Dashboard PO rows.
* **Design File Reference:** `[Link to PO Details Modal Frame/Artboard - TBP]`

---

#### Assign Serial Number Modal (New)

* **Purpose:** Capture required serial number before entering Powder Coat.
* **Key Elements:**
    * Modal Title (e.g., "Assign Serial for Powder Coat"). Pump context display (Model, PO, Cust).
    * Single input field for 4-digit Serial Number. Error display area.
    * Footer ("Save", "Cancel").
* **Interaction Notes:** Triggered by specific Kanban drag. "Save" performs uniqueness validation before calling store action.
* **Design File Reference:** `[Link to Assign Serial Modal Frame/Artboard - TBP]`

---

## Component Library / Design System

* **Design System Approach:** Build components locally using **ShadCN/ui** primitives, **Tailwind CSS**, and **Framer Motion**, adhering to style/motion guidelines and quality constraints. `docs/UI-Guidelines.md` serves as inspiration and reference. **21st.dev Magic** is an optional source.

---

### Core Components

#### Pump Card

* **Purpose:** Display pump info on Kanban. Must use ShadCN primitives.
* **Variants:** Expanded, Collapsed.
* **States:** Default, Hover, Press/Drag, Focus.
* **Usage Guidelines:** Draggable (`@dnd-kit`). Double-clickable. Shows Priority. Handles missing serial numbers gracefully. ARIA required. JSDoc required.

#### Filter Bar

* **Purpose:** Global filtering controls.
* **Variants:** In toolbar.
* **States:** Standard input states (ShadCN primitives).
* **Usage Guidelines:** Uses ShadCN `Select`/`Input`. Has "Clear" button. Updates Zustand store immediately. Keyboard navigable.

#### KPI Widget

* **Purpose:** Display single metric on Dashboard. Must use ShadCN primitives.
* **Variants:** Standard display (Title, Value, Unit/Icon).
* **States:** Default, Hover.
* **Usage Guidelines:** Animates value on load (Framer Motion recipe). JSDoc required.

#### Modal Dialog (Base)

* **Purpose:** Consistent container for all modal types.
* **Variants:** Standard layout (Title, Body, Footer).
* **States:** Open, Closed.
* **Usage Guidelines:** Built using ShadCN `Dialog`. Uses standard entry/exit animations (Framer Motion recipe). Manages focus trapping and keyboard interactions.

---

## Branding & Style Guide

This section outlines the visual and stylistic elements for PumpTracker Lite, ensuring a consistent and high-quality user interface.

### Visual Identity

* **Brand Guidelines:** No formal external brand guidelines. Aim for a **clean, modern, professional aesthetic** inspired by `docs/UI-Guidelines.md`.
* **Visual Structure & Depth:** Draw inspiration from the **Layer Stack concept** and shadow recommendations in `docs/UI-Guidelines.md`.
* **Glass Effects:** Use sparingly per guidance in `docs/UI-Guidelines.md`.
* **Accessibility:** All text/UI color combinations **must** meet WCAG AA contrast ratios.

---

### Color Palette

Defined in `tailwind.config.js`.

| Color Type  | Hex Code / Tailwind Class                          | Usage                                                                 |
| :---------- | :------------------------------------------------- | :-------------------------------------------------------------------- |
| Primary     | `#0158A7` / `bg-blue-700`                           | Main actions, highlights, active states, header bars                  |
| Secondary   | `#023E73` / `bg-blue-900`                           | Secondary actions, sidebars, hover states                             |
| Accent      | `#FFD200` / `bg-yellow-400`                        | MSP highlight color — CTAs, hover accents, subtle highlights          |
| Success     | `#22C55E` / `bg-green-500`                          | Positive feedback, confirmations                                      |
| Warning     | `#FACC15` / `bg-yellow-500`                         | Cautions, alerts, pending actions                                     |
| Error       | `#DC2626` / `bg-red-600`                            | Errors, destructive actions                                           |
| Neutral     | `#E5E7EB` to `text-gray-600` / `bg-gray-200` etc. | Text, borders, icons, dividers (use darker for text, lighter for borders) |
| Backgrounds | `#F9FAFB`/`bg-gray-50`, `#FFFFFF`/`bg-white`, `#1E293B`/`bg-slate-800` (dark L3) | Layered surfaces: L3 Background, L2 Swimlane, L1 Cards |

*(Dev team updates `tailwind.config.js` during setup.)*

#### Dark Mode Strategy

* Support dark mode using Slate 800 (`#1E293B`) background.
* Use light neutrals (white, light grays) for text/borders with sufficient contrast.
* **Retain brand identity using shades of Primary Blue (`#0158A7`) and Accent Yellow (`#FFD200`)** for key elements/highlights, ensuring accessibility. Define specific mappings in Tailwind config.

---

### Typography

Managed via `tailwind.config.js`.

* **Font Families:**
    * **Primary (Sans-serif):** `Inter` (Recommended).
    * **Monospace:** `JetBrains Mono` (Recommended).
* **Type Scale:** (e.g., H1 page titles, H2 sections, H3 cards)

| Element | Size       | Weight       | Line Height      |
| :------ | :--------- | :----------- | :--------------- |
| H1      | `text-3xl` | `font-bold`  | `leading-tight`  |
| H2      | `text-2xl` | `font-semibold`| `leading-tight`  |
| H3      | `text-lg`  | `font-semibold`| `leading-normal` |
| Body    | `text-base`| `font-normal`| `leading-relaxed`|
| Small   | `text-sm`  | `font-normal`| `leading-snug`   |

*(Dev team updates `tailwind.config.js` during setup.)*

---

### Iconography

* **Icon Library:** Use **Lucide Icons** (`lucide-react`).
* **Usage Guidelines:** Use purposefully for clarity. Ensure proper sizing/alignment.

---

### Spacing & Layout

* **Grid System:** Standard Tailwind grid classes for page structure.
* **Spacing Scale:** All spacing **must** use configured Tailwind scale (`p-4`, `m-2`, `gap-6`). No arbitrary values.

---

## Accessibility Requirements

### Compliance Target

* **Standard:** Aim for **WCAG 2.1 Level AA** compliance.

---

### Key Requirements

* **Visual:** AA Contrast Ratios enforced. Visible focus indicators required. Relative text units.
* **Interaction:** Full keyboard navigation required. Semantic HTML + ARIA required. Adequate touch targets. **Keyboard alternative for drag-and-drop**.
* **Content:** Alt text for meaningful images. Correct heading structure. Labels for all form inputs.

---

### Testing Strategy

* Automated linting (`eslint-plugin-jsx-a11y`).
* Manual keyboard testing.
* Basic screen reader testing.
* Contrast checks during dev/review.

---

## Responsiveness Strategy

Focus on tablet/desktop; basic mobile usability.

### Breakpoints

Standard Tailwind breakpoints (sm, md, lg, xl+).

| Breakpoint | Min Width | Max Width   | Target Devices                       | Notes                                  |
| :--------- | :-------- | :---------- | :----------------------------------- | :------------------------------------- |
| Mobile (sm)| `640px`   | `767px`     | Small tablets, large phones (landscape) | Basic functionality, some scrolling okay |
| Tablet (md)| `768px`   | `1023px`    | Tablets (portrait & landscape)       | Primary target alongside Desktop       |
| Desktop (lg)|`1024px`   | `1279px`    | Laptops, smaller desktop monitors    | Primary target                         |
| Wide (xl+) | `1280px+` | -           | Larger desktop monitors              | Utilize extra space, avoid excessive width |

*(Note: Assumes Tailwind defaults. Specific values can be customized in `tailwind.config.js` if needed.)*

---

### Adaptation Patterns

* **Layout:** Stack vertically on smaller screens. Horizontal scrolling acceptable on mobile for complex elements (Table, Kanban).
* **Navigation:** Persistent header/toolbar adapts as needed (e.g., menu collapse).
* **Content:** Prioritize critical info visibility.
* **Interaction:** Ensure touch targets adequate; DnD functional on touch.

---

## Animation & Micro-interactions

Leverage **Framer Motion** purposefully and consistently.

### Motion Principles

* Purposeful, Subtle & Quick, Performant, Consistent.
* **Adherence to `docs/UI-Guidelines.md` Motion Recipes is required**.

---

### Key Animations (Based on Motion Recipes)

* Card Hover.
* Card Press/Drag.
* Element Entry (Staggered).
* KPI Reveal.
* Modal Entry/Exit.
* Kanban Drag Enhancements.

---

## Performance Considerations

### Performance Goals

* Fast initial load (< 3s).
* Responsive interactions (< 200ms).
* Smooth animations (60 FPS).

---

### Design Strategies

* Minimize assets.
* Efficient data handling (memoization, debouncing).
* Virtualization if needed (post-MVP).
* Performant animations.

---

## Next Steps

### Immediate Actions

1.  **Stakeholder Review:** Share this UI/UX Spec for review/approval.
2.  **Visual Design:** Proceed with detailed mockups in design tool. Finalize Font Families, Dark Mode mappings.
3.  **Tailwind Configuration:** Update `tailwind.config.js` during project setup.
4.  **Architectural Handoff:** Provide this doc + PRD to Architect (Winston).

---

### Design Handoff Checklist

* [X] User flows documented
* [X] Component inventory defined
* [X] Accessibility requirements defined
* [X] Responsive strategy clear
* [X] Brand guidelines incorporated
* [X] Performance goals established
* [X] Motion principles defined