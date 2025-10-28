# 🤩 PumpTracker Lite — Updated Product Requirements Document (v2.2)

## Purpose
Build a **lightweight, local-first prototype** to validate the PumpTracker concept using a focused, single-user interface. Prioritize speed, usability, and a realistic production flow simulation.

---

## 🎯 Goals
### Business Goals
* Validate feasibility of PumpTracker concept with real workflows.
* Identify pain points in visual order tracking and data input.
* Enable stakeholders to iterate rapidly on real data without backend bottlenecks.

### User Goals
* Quickly see overall job status (Dashboard).
* Manage pump orders through production (Kanban).
* Add new jobs seamlessly via "Add PO" modal, leveraging model defaults.
* Assign required serial numbers at the correct workflow step (before Powder Coat).
* Experience a clean, modern, and high-quality user interface adhering to defined style and motion guidelines.
* Plan for future upload/verify workflow once MVP stabilizes.


### Non-Goals
* Multi-user support or collaboration.
* Authentication or permissions logic.
* Full mobile responsiveness.
* In-app UI for managing Model defaults (MVP uses `models.json`).

---

## 🧭 User Flow
1.  Launch app → User lands on **Dashboard page** (`/dashboard`).
2.  Use **navigation bar** to access:
    * 📊 Dashboard (`/dashboard`)
    * 🗂️ Kanban Board (`/kanban`)
3.  **Persistent header** includes:
    * Global filter bar (Dashboard & Kanban).
    * 🔍 Search bar (pill-shaped input that filters live).
    * 🔘 "Add PO" button → opens modal to enter:
        * PO #, Customer, Date Received, PO-Level Promise Date.
        * **Normalized Line Items:** Model, Quantity, Color, Priority, Value (default from Model, editable), Line Promise Date (override). **Serial numbers are NOT entered here.**.
        * Generated `Pump` cards inherit metadata from lines & linked `Model` (value, buildTime, BOM).
4.  From **Dashboard**:
    * Users see KPI widgets, charts, timeline, and a PO-expanded pump list.
    * Double-click:
        * PO row → opens PO Details Modal.
        * Pump row → opens Pump Details Modal.
5.  From **Kanban**:
    * Users drag/drop pumps through lifecycle stages. **Stage moves generate historical `PumpEvent` records.**.
    * **If dragging a pump *without* a serial number to "POWDER COAT", user is prompted by the "Assign Serial Number" modal.**.
    * Double-click pump card → open Pump Details Modal.
6.  **Serial Number Assignment:** Users can add/edit the (optional but required by Powder Coat) serial number via the **Pump Details Modal** or the **Assign Serial Number Modal** prompt. **Uniqueness is enforced.**.
7.  Future enhancement: **Upload & Verify** route returns post-MVP for bulk data management.

---

## 🤩 Core MVP Features

### 1. Global Navigation
* Nav bar locked to top of viewport.
* Links to: Dashboard | Kanban (Upload reserved for post-MVP).
* Filter bar + Search + Add PO always visible.

### 2. Dashboard (Page: `/dashboard`)
* **KPI Strip**: (Calculations may leverage `PumpEvent` data for accuracy)
    * Avg Build Time
    * On-Time %
    * Shop Efficiency
    * Avg Weekly Ship Count
    * Avg Weekly Value ($)
* **Workload Donuts**: Pumps by Customer, Model.
* **Trend**: Build time by week (AreaChart).
* **Capacity Radials**: Weekly demand vs capacity.
* **Timeline (Gantt-lite)**: Pump-level timeline by promise date or priority. *(Note: May be removed post-MVP)*.
* **PO + Pump List Table**:
    * Expandable rows per PO.
    * Row double-click opens respective modal (Pump or PO).

### 3. Kanban Board (Page: `/kanban`)
* 6 stages as columns (`NOT STARTED`, `FABRICATION`, `POWDER COAT`, `ASSEMBLY`, `TESTING`, `SHIPPING`).
* Pump card display order: Model, Customer, Serial # (or placeholder), PO.
* Priority = colored circle indicator.
* Collapsed state: Shows Model, Customer, Serial (or placeholder). Smaller footprint.
* Drag/drop via `@dnd-kit`. **Creates `PumpEvent` on stage change.**.
* **Triggers "Assign Serial Number" modal if moving pump without serial to "POWDER COAT".**.
* Double-click = Pump Details Modal.

### 4. Add PO Modal
* Opened from header "Add PO" button.
* Fields:
    * PO #, Customer, Date Received, PO-Level Promise Date.
    * **Normalized Lines:** Model, Quantity, Powder Color, Priority, Value (default from `Model`, editable), Line Promise Date (override).
* Submit = Creates `PurchaseOrder`, `PurchaseOrderLine[]`, and N `Pump` objects (state: "NOT STARTED", **serial undefined**, defaults from `Model`).

### 5. Pump Details Modal
* Editable modal.
* Double-click opens from Kanban or Dashboard row.
* Shows metadata: PO, **Serial (editable, optional, unique)**, Model, Stage, Value, **Build Time**, **BOM (viewable)**, Dates, etc..
* Edit mode via "Edit" button.
* **Serial uniqueness validated on save.**.

### 6. Purchase Order Details Modal
* Opens from Dashboard PO row double-click.
* Shows PO fields and **associated `PurchaseOrderLine` items**. Lists linked pumps.
* Read-only initially; "Edit" toggles edit mode for PO fields and **line item values** (with optional pump propagation).

### 7. Assign Serial Number Modal (New)
* **Purpose:** Capture required serial number before Powder Coat.
* **Trigger:** Dragging pump without serial to "POWDER COAT".
* **Fields:** Pump context, Serial input, Error display.
* **Validation:** **Uniqueness check required on save.**.
* **Actions:** Save (updates pump serial & stage, creates PumpEvent), Cancel.

---

## 🔍 Filters
* Apply via header filter bar.
* **Affects Dashboard and Kanban**.
* Fields: PO, Customer, Model, Stage, Priority, Free text.
* Clear All resets instantly (<100ms).

---

## 📊 Success Metrics
* ⚙️ Runs locally with seed data and `models.json`.
* 📈 Accurate KPI & chart rendering (potentially using `PumpEvent` data).
* 🤩 Add PO → pumps appear correctly (with defaults from Model, no initial serial).
* ⏩ Drag/drop pumps works smoothly, **triggers serial prompt correctly**, creates `PumpEvent`.
* ⌨️ Keyboard accessible modals & navigation.
* 💵 Default pricing auto-populates from `Model` entity, remains editable.
* 🔢 Serial numbers can be added/edited via Modals, **uniqueness enforced**, required by Powder Coat stage.

---

## 🧠 Technical Considerations
* **Core Stack:** React 19, Vite, TypeScript, Zustand for global state.
* **UI Implementation Stack:** ShadCN/UI primitives + Tailwind CSS for styling.
* **Drag & Drop:** `@dnd-kit` for Kanban interactions.
* **Charting:** Recharts primitives only.
* **Data Source (Models):** Reads `src/data/models.json` for model defaults (price, buildTime, BOM).
* **Future Upload:** `PapaParse` reserved for post-MVP upload feature.
* **Motion:** **Framer Motion** required, **must** follow Motion Recipes in `docs/UI-Guidelines.md`.
* **Persistence:** LocalStorage (default via `LocalAdapter`), optional Supabase adapter. Adapters handle **normalized structure** (`purchaseOrderLines`, `pumpEvents`) and **hygiene** (versioning, timestamps). **Zod** recommended for `LocalAdapter` load validation.
* **Implementation Constraints:** Development **must** adhere to defined standards: use ShadCN primitives, style strictly with Tailwind tokens, follow Layer Stack/Motion Recipes (`docs/UI-Guidelines.md`), implement accessibility (WCAG AA), include JSDoc.

---

## 🧱 Architecture Updates
* Use **React Router** for routes: `/dashboard`, `/kanban` (`/upload` post-MVP).
* Zustand store handles shared state: `pumps`, `purchaseOrders`, **`purchaseOrderLines`**, **`pumpEvents`**, `filters`, `collapsedStages`, **`models`**.
* Persisted to `localStorage` (default) via `LocalAdapter` or optionally Supabase via `SupabaseAdapter`. Adapters handle **normalized structure and event creation**.
* Add PO, Filters, Kanban interactions, modal edits write to shared state. Stage moves create `PumpEvent` records.

---

## ✨ Post-MVP Vision
*(No changes from previous version - already included BOM, Scheduling, Upload, Model Mgmt UI)*.

* **BOM Integration & Inventory Alerting**
* **Dedicated Scheduling Page** (Fabrication Calendar & Full Gantt)
* **Bulk Data Upload & Verification**
* **Model Data Management UI**

---

## 📆 Milestones
* **Week 1**: Routing + Layout + Zustand store (**inc. Model loading, normalized state**).
* **Week 2**: Dashboard widgets + charts + KPI logic (**using PumpEvents where applicable**).
* **Week 3**: Kanban Board + Drag/Drop (**with serial prompt, event creation**) + Base Modals.
* **Week 4**: Add PO Modal (using Model defaults, normalized lines) + PO/Pump Details Modals (**serial editing/validation**) + Final polish + seed data test.
* **Post-MVP**: Scheduling Page, Upload Page, BOM Inventory, Model Management UI.

---

## ❌ Out of Scope
* Auth / user accounts.
* Mobile-first layout.
* Realtime sync.
* Server-side validation (MVP uses client-side).
* In-app UI for managing Model defaults (MVP uses `models.json`).

---

## 🧪 Acceptance Criteria
* Add PO adds correct `PurchaseOrder`, `PurchaseOrderLine[]`, and `Pump[]` (with defaults from Model, no initial serial).
* Filters update Dashboard & Kanban.
* Dashboard shows correct stats (reflecting `PumpEvents` where needed).
* Kanban drag-drop updates state, creates `PumpEvent`, **prompts for serial correctly before Powder Coat**, drives shipping metrics.
* Double-click opens modal with editable details.
* Serial numbers can be added/edited via Modals, **uniqueness enforced**.
* No view switch without navigation.