# Manufacturing UI: Control Interfaces

Design patterns for industrial control interfaces that balance functionality, safety, and usability in manufacturing environments.

## Control Interface Philosophy

### Industrial Control Principles

Control interfaces must prioritize:

- **Clarity**: Immediate understanding of control state and function
- **Safety**: Clear indication of critical operations and consequences
- **Efficiency**: Minimal cognitive load for frequent operations
- **Feedback**: Immediate confirmation of user actions
- **Error Prevention**: Design that prevents incorrect operations

### Environmental Considerations

Manufacturing environments present unique challenges:

- **Variable Lighting**: From bright factory floors to dim control rooms
- **Noise Considerations**: Visual feedback must compensate for noisy environments
- **Glove Usage**: Controls must work with industrial gloves
- **Critical Timing**: Operations may be time-sensitive
- **Multi-Tasking**: Users often monitor multiple systems simultaneously

## Control Layout Patterns

### 1. Standard Control Panel Layout

#### Zone-Based Organization
```css
.control-panel {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: auto 1fr auto;
  gap: 16px;
  height: 100vh;
  padding: 16px;
}

.control-panel__header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-panel__primary {
  /* Main operational controls */
}

.control-panel__status {
  /* System status and monitoring */
}

.control-panel__secondary {
  /* Utility and configuration controls */
}

.control-panel__footer {
  grid-column: 1 / -1;
  /* System-wide controls and information */
}
```

#### Control Grouping Strategy
```css
.control-group {
  background: var(--surface-primary);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.control-group__header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-subtle);
}

.control-group__title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.control-group__status {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group__content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

### 2. Control Component Patterns

#### Primary Action Controls
```css
.primary-control {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 2px solid var(--border-subtle);
  border-radius: 8px;
  background: var(--surface-primary);
  transition: all 0.2s ease-out;
  cursor: pointer;
}

.primary-control:hover {
  border-color: var(--accent-operational);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.primary-control:active {
  transform: translateY(0);
}

.primary-control__icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--text-primary);
  background: var(--surface-secondary);
  border-radius: 50%;
  transition: all 0.2s ease-out;
}

.primary-control:hover .primary-control__icon {
  background: var(--accent-operational);
  color: white;
}

.primary-control__label {
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  color: var(--text-primary);
}

.primary-control__status {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--status-normal);
}

.primary-control.danger .primary-control__icon {
  background: var(--status-error);
  color: white;
}

.primary-control.danger:hover {
  border-color: var(--status-error);
}
```

#### Slider Controls for Continuous Values
```css
.slider-control {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--surface-secondary);
  border-radius: 6px;
}

.slider-control__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.slider-control__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.slider-control__value {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-operational);
  min-width: 48px;
  text-align: right;
}

.slider-control__track {
  position: relative;
  height: 8px;
  background: var(--border-subtle);
  border-radius: 4px;
  cursor: pointer;
}

.slider-control__progress {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: var(--accent-operational);
  border-radius: 4px;
  transition: width 0.2s ease-out;
}

.slider-control__thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 24px;
  height: 24px;
  background: white;
  border: 3px solid var(--accent-operational);
  border-radius: 50%;
  cursor: grab;
  transition: all 0.2s ease-out;
}

.slider-control__thumb:hover {
  transform: translate(-50%, -50%) scale(1.1);
}

.slider-control__thumb:active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.2);
}

/* Critical value indicators */
.slider-control.critical .slider-control__progress {
  background: var(--status-warning);
}

.slider-control.critical .slider-control__thumb {
  border-color: var(--status-warning);
}
```

### 3. Status and Feedback Patterns

#### System Status Indicators
```css
.status-panel {
  background: var(--surface-primary);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-subtle);
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--surface-tertiary);
}

.status-item:last-child {
  border-bottom: none;
}

.status-item__info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-item__indicator {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  position: relative;
}

.status-item__indicator::before {
  content: '';
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease-out;
}

.status-item__indicator.active::before {
  opacity: 0.3;
  animation: status-pulse 2s ease-in-out infinite;
}

.status-item__details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-item__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.status-item__value {
  font-size: 14px;
  color: var(--text-secondary);
}

.status-item__timestamp {
  font-size: 11px;
  color: var(--text-tertiary);
}

/* Status color variants */
.status-item__indicator.normal {
  background: var(--status-normal);
}

.status-item__indicator.warning {
  background: var(--status-warning);
}

.status-item__indicator.error {
  background: var(--status-error);
}
```

#### Alert and Warning Systems
```css
.alert-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border-left: 4px solid;
}

.alert-banner.info {
  background: rgba(59, 130, 246, 0.1);
  border-left-color: var(--accent-operational);
  color: var(--accent-operational);
}

.alert-banner.warning {
  background: rgba(245, 158, 11, 0.1);
  border-left-color: var(--status-warning);
  color: var(--status-warning);
}

.alert-banner.error {
  background: rgba(239, 68, 68, 0.1);
  border-left-color: var(--status-error);
  color: var(--status-error);
}

.alert-banner.critical {
  background: rgba(220, 38, 38, 0.1);
  border-left-color: var(--warning-critical);
  color: var(--warning-critical);
  animation: critical-pulse 1s ease-in-out infinite;
}

@keyframes critical-pulse {
  0%, 100% {
    background: rgba(220, 38, 38, 0.1);
  }
  50% {
    background: rgba(220, 38, 38, 0.2);
  }
}

.alert-banner__icon {
  font-size: 20px;
  flex-shrink: 0;
}

.alert-banner__content {
  flex: 1;
}

.alert-banner__title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 2px;
}

.alert-banner__message {
  font-size: 13px;
  line-height: 1.4;
}

.alert-banner__actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
```

### 4. Safety-Critical Controls

#### Emergency Stop Patterns
```css
.emergency-stop {
  position: relative;
  width: 120px;
  height: 120px;
  background: var(--warning-critical);
  border-radius: 50%;
  border: 4px solid var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease-out;
  box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
}

.emergency-stop:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 30px rgba(220, 38, 38, 0.5);
}

.emergency-stop:active {
  transform: scale(0.95);
}

.emergency-stop__label {
  color: white;
  font-weight: 700;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-align: center;
}

.emergency-stop__icon {
  font-size: 32px;
  color: white;
  margin-bottom: 4px;
}

/* Protection against accidental activation */
.emergency-stop.confirming {
  animation: confirm-pulse 0.5s ease-in-out;
}

@keyframes confirm-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
```

#### Two-Stage Critical Controls
```css
.critical-control {
  position: relative;
}

.critical-control__trigger {
  padding: 12px 24px;
  background: var(--surface-secondary);
  border: 2px solid var(--border-subtle);
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.critical-control__trigger:hover {
  border-color: var(--warning-critical);
  background: rgba(220, 38, 38, 0.1);
}

.critical-control__confirm {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  display: none;
  gap: 8px;
  z-index: 10;
}

.critical-control.confirming .critical-control__confirm {
  display: flex;
}

.critical-control__confirm-button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease-out;
}

.critical-control__confirm-button.confirm {
  background: var(--warning-critical);
  color: white;
}

.critical-control__confirm-button.cancel {
  background: var(--surface-tertiary);
  color: var(--text-primary);
}

.critical-control__confirm-button:hover {
  transform: translateY(-1px);
}
```

## Implementation Guidelines

### Control Standards

#### Spacing and Size Standards
```css
:root {
  /* Control sizing for industrial environments */
  --control-min-touch-target: 44px;    /* Minimum touch target size */
  --control-spacing: 16px;             /* Standard spacing between controls */
  --control-group-spacing: 24px;       /* Spacing between control groups */
  --critical-control-size: 120px;      /* Emergency control size */

  /* Typography for controls */
  --control-label-size: 12px;          /* Small, clear labels */
  --control-value-size: 14px;          /* Clear value display */
  --status-text-size: 11px;            /* Status and timestamp text */
}
```

#### Color Coding Standards
```css
:root {
  /* Industrial safety colors */
  --safety-red: #dc2626;               /* Stop, danger, emergency */
  --safety-orange: #ea580c;            /* Warning, caution */
  --safety-yellow: #facc15;            /* Alert, attention */
  --safety-blue: #2563eb;              /* Information, instruction */
  --safety-green: #16a34a;             /* Safe, go, normal */

  /* Control state colors */
  --control-active: #059669;           /* Active/running state */
  --control-inactive: #6b7280;         /* Inactive/stopped state */
  --control-error: #dc2626;            /* Error/fault state */
  --control-warning: #d97706;          /* Warning/caution state */
}
```

### Accessibility and Usability

#### High Contrast Support
```css
@media (prefers-contrast: high) {
  .control-panel {
    background: white;
    color: black;
  }

  .control-group {
    border: 2px solid black;
  }

  .primary-control {
    border: 2px solid black;
  }
}

/* Keyboard navigation support */
.primary-control:focus,
.slider-control:focus {
  outline: 3px solid var(--accent-operational);
  outline-offset: 2px;
}
```

#### Reduced Motion Support
```css
@media (prefers-reduced-motion: reduce) {
  .primary-control,
  .slider-control__thumb,
  .status-item__indicator::before {
    transition: none;
    animation: none;
  }
}
```

## Testing and Validation

### Control Usability Testing

#### Key Test Areas
- **Glove Compatibility**: Can controls be operated with industrial gloves?
- **Lighting Conditions**: Are controls visible in various lighting?
- **Error Prevention**: Are accidental operations minimized?
- **Clarity**: Is control function immediately obvious?
- **Feedback**: Is action confirmation clear and immediate?

#### Performance Testing
```javascript
// Control responsiveness testing
const measureControlResponse = (control) => {
  const startTime = performance.now();

  control.addEventListener('click', () => {
    const responseTime = performance.now() - startTime;

    // Log for optimization
    if (responseTime > 100) {
      console.warn('Control response time exceeds 100ms');
    }
  });
};
```

## Common Mistakes to Avoid

### Safety Issues
- ❌ Uncritical controls with emergency styling
- ❌ Accidental activation prevention missing
- ❌ Insufficient feedback for critical operations
- ❌ Inconsistent safety color usage

### Usability Problems
- ❌ Controls too close together
- ❌ Insufficient contrast in industrial environments
- ❌ Unclear control labeling or icons
- ❌ Poor feedback on control state changes

### Performance Issues
- ❌ Slow control response times
- ❌ Excessive animations on controls
- ❌ Complex control hierarchies
- ❌ Inefficient state management

This control interface framework provides the foundation for creating safe, efficient, and professional industrial control systems that support manufacturing operations effectively.