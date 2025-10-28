# PumpTracker Lite - Project Knowledge Base

## Project Overview
**Project Name**: PumpTracker Lite  
**Type**: Manufacturing Workflow Management System  
**Status**: MVP Development Phase  
**Location**: ai_working/new-project/

## Core Purpose
PumpTracker Lite is a lightweight, local-first application for tracking pump orders through production stages. It provides a simplified view of manufacturing operations with two main views: Dashboard for analytics and Kanban board for visual workflow management.

## Key Technical Architecture

### Frontend Stack
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **ShadCN/ui** for component library
- **Framer Motion** for animations
- **Zustand** for state management
- **React Query** for server state
- **Recharts** for data visualization

### Backend/Data Layer
- **Tauri** for desktop application packaging
- **JSON files** for local data persistence
- **localStorage** for real-time state
- **Supabase** (optional) for cloud sync
- **Node.js/Express** optional REST API

### Data Models
- **Purchase Orders**: Header-level information with normalized line items
- **Pumps**: Individual units generated from PO line items
- **PumpEvents**: Timestamped stage transitions
- **Models**: Default configurations (pricing, lead times, BOM)
- **Customers**: Directory of rental companies

## Core Features & Workflows

### 1. Dashboard View (/dashboard)
**Purpose**: High-level production overview and analytics

**Key Components**:
- KPI Strip (Average Build Time, On-Time % Daily Efficiency, Ship Count, Total Value)
- Workload Donut Charts (Pumps by Customer, Pumps by Model)
- Build Time Trend Area Chart (7-day rolling average)
- Capacity Radial Charts (Weekly demand vs capacity visualization)
- Expandable PO/Pump Table (Double-click for details)

**Data Calculations**:
- Average Build Time: `SUM(build_time) / COUNT(completed_pumps)`
- Daily Efficiency: `actual_output / planned_capacity`
- On-Time Percentage: `on_time_deliveries / total_deliveries`

### 2. Kanban Board View (/kanban)
**Purpose**: Visual management of pumps through production stages

**Production Stages**:
1. **NOT STARTED** - Initial state for all pumps
2. **FABRICATION** - Manufacturing phase
3. **POWDER COAT** - Surface finishing (serial number required)
4. **ASSEMBLY** - Component assembly
5. **TESTING** - Quality assurance and performance testing
6. **SHIPPING** - Final packaging and shipment preparation

**Key Features**:
- Drag-and-drop pump cards between stages
- Collapsible stage columns with item counts
- Real-time global filtering by customer, model, priority
- Double-click cards for pump details modal

### 3. Purchase Order Management
**Add PO Modal Workflow**:
1. User clicks "Add PO" button
2. Modal opens with PO-level fields (PO #, Customer, Dates)
3. Dynamic line items section for pump specifications
4. Form validation before submission
5. Systems expands line items into individual pump records
6. New pumps appear in "NOT STARTED" column

**Line Item Fields**:
- Model selection (from predefined catalog)
- Quantity (number of identical pumps)
- Priority level (1-5 scale)
- Color/finish specification
- Value (auto-populated from model defaults)
- Line-specific promise dates

### 4. Serial Number Management
**Business Rule**: Serial numbers are required before pumps enter Powder Coat stage

**Implementation**:
- 4-digit unique identifier format
- Uniqueness validation across all pumps
- Contextual assignment via modal when dragging to Powder Coat
- Direct editing through Pump Details modal

## Data Structure & Relationships

### Entity Relationships
```
Purchase Order (1) → (n) Line Items
Line Item (1) → (n) Pumps
Pump (1) → (n) Pump Events
Model (1) → (n) Pumps
Customer (1) → (n) Purchase Orders
```

### Key Data Fields
**PurchaseOrder**: id, po_number, customer_id, order_date, promise_date, notes  
**LineItem**: id, po_id, model_id, quantity, priority, color, value_each, line_promise_date  
**Pump**: id, line_item_id, serial_number, stage, priority, color, current_stage_start_date  
**PumpEvent**: id, pump_id, from_stage, to_stage, timestamp, notes

## Manufacturing Domain Knowledge

### Pump Models Catalog
**Diaphragm Pumps**: DD-4S, DD-4S SAFE, DD-6, DD-6 SAFE, DV-6  
**Rotary Lobe Pumps**: RL200, RL200-SAFE, RL300, RL300-SAFE  
**Centrifugal Pumps**: HC-150, HC-150-SAFE, PP-150, SIP-150, DP-150, HP-150  

**Standard Lead Times** (business days):
- Fabrication: 1.5-2.0 days
- Powder Coat: 7.0 days (bottleneck stage)
- Assembly: 1.0-1.25 days
- Testing: 0.25 days
- Total: 9.75-11.25 days

### Customer Base
Primary customers are equipment rental companies:
- United Rentals, Sunbelt Rentals, Herc Rentals
- Regional companies: Valencourt, Rain For Rent, Equipment Share
- CAT dealerships: Carter CAT, Ring Power CAT, Thompson CAT

## User Experience Design

### Design Principles
1. **Clarity First** - Information display over visual complexity
2. **Efficiency in Action** - Minimize clicks for core workflows
3. **Visual Consistency** - Cohesive aesthetic using ShadCN/ui
4. **Responsive Feedback** - Immediate visual feedback for all actions
5. **Focus on Core** - Clean interface centered on primary tasks

### Accessibility Requirements
- WCAG 2.1 Level AA compliance
- Full keyboard navigation including drag-and-drop alternatives
- Screen reader compatibility
- High contrast color combinations
- Adequate touch targets (44px minimum)

### Performance Targets
- Initial load: < 3 seconds
- Interaction response: < 200ms
- Smooth animations: 60 FPS
- Efficient data handling with memoization

## Implementation Strategy

### MVP Scope (Initial Release)
- ✅ Dashboard with KPIs and basic charts
- ✅ Kanban board with drag-and-drop
- ✅ Purchase Order creation and management
- ✅ Pump details modal with serial number assignment
- ✅ Real-time filtering and search
- ✅ Local data persistence with JSON files

### Future Enhancements (Post-MVP)
- Timeline view (Gantt chart visualization)
- Advanced analytics and reporting
- Cloud sync with Supabase integration
- Mobile responsive design
- Export capabilities (PDF, Excel)
- User authentication and permissions

## Technical Implementation Notes

### State Management Architecture
```
Global Store (Zustand)
├── purchases: PurchaseOrder[]
├── pumps: Pump[]
├── models: Model[]
├── customers: Customer[]
├── filters: FilterState
└── ui: UIState (loading, modals, etc.)
```

### Data Adapter Pattern
- **DataAdapter**: Interface for persistence operations
- **LocalStorageAdapter**: JSON-based local storage
- **SupabaseAdapter**: Optional cloud sync (future)
- **MockAdapter**: Development and testing

### Component Architecture
```
src/
├── components/
│   ├── ui/          # ShadCN/ui base components
│   ├── dashboard/   # Dashboard-specific components
│   ├── kanban/      # Kanban board components
│   └── shared/      # Reusable components
├── stores/          # Zustand store definitions
├── types/           # TypeScript type definitions
├── utils/           # Helper functions
└── data/            # JSON data files and adapters
```

## Quality Assurance Considerations

### Critical Test Scenarios
1. **Purchase Order Creation**: Form validation, line item expansion
2. **Kanban Drag-and-Drop**: Stage transitions, serial number validation
3. **Data Persistence**: Save/load cycles, data integrity
4. **Filtering Logic**: Multi-criteria filtering performance
5. **KPI Calculations**: Accuracy of dashboard metrics

### Error Handling Patterns
- Graceful degradation for data loading failures
- User-friendly error messages with context
- Automatic retry for transient failures
- Data validation at both client and persistence layers

This knowledge base serves as the comprehensive reference for PumpTracker Lite development, capturing all essential project information for AI-assisted development workflows.