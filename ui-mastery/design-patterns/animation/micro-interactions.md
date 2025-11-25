# Animation: Micro-Interactions

Subtle, purposeful animations that enhance user experience without overwhelming the interface, specifically designed for manufacturing and industrial applications.

## Micro-Interaction Philosophy

### Purpose-Driven Animation

Every animation should serve a specific purpose:

- **Feedback**: Acknowledge user actions and system responses
- **Guidance**: Direct attention to important changes or elements
- **Status**: Indicate loading, processing, or system states
- **Delight**: Add personality without compromising functionality
- **Clarity**: Make state changes more obvious and understandable

### Industrial Animation Principles

For manufacturing environments, animations must be:

- **Subtle**: Not distracting during critical operations
- **Fast**: Respect user time and efficiency requirements
- **Clear**: Meaning is immediately apparent
- **Consistent**: Similar actions have similar animations
- **Accessible**: Respect user motion preferences

## Essential Micro-Interactions

### 1. Button Interactions

#### Basic Button Press
```css
.manufacturing-button {
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.manufacturing-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.manufacturing-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Ripple effect for touch feedback */
.manufacturing-button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.manufacturing-button:active::after {
  width: 300px;
  height: 300px;
}
```

#### Status Change Buttons
```css
.status-button {
  transition: all 0.2s ease-out;
}

.status-button--success {
  background-color: var(--status-normal);
  animation: status-confirm 0.4s ease-out;
}

.status-button--error {
  background-color: var(--status-error);
  animation: status-error 0.4s ease-out;
}

@keyframes status-confirm {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

@keyframes status-error {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-2px); }
  20%, 40%, 60%, 80% { transform: translateX(2px); }
}
```

### 2. Loading and Processing States

#### Progress Indicators
```css
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-subtle);
  border-top: 2px solid var(--accent-operational);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Pulsing indicator for long operations */
.loading-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--accent-operational);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.1);
  }
}
```

#### Skeleton Loading
```css
.skeleton-loading {
  background: linear-gradient(
    90deg,
    var(--surface-secondary) 0%,
    var(--surface-tertiary) 50%,
    var(--surface-secondary) 100%
  );
  background-size: 200% 100%;
  animation: skeleton 1.5s ease-in-out infinite;
}

@keyframes skeleton {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

### 3. Data Input Interactions

#### Input Field Focus
```css
.industrial-input {
  transition: all 0.2s ease-out;
  border: 2px solid var(--border-subtle);
}

.industrial-input:focus {
  border-color: var(--accent-operational);
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
  transform: translateY(-1px);
}

.industrial-input:valid {
  border-color: var(--status-normal);
}

.industrial-input:invalid {
  border-color: var(--status-error);
}
```

#### Numeric Input Controls
```css
.number-input-control {
  transition: all 0.15s ease-out;
  cursor: pointer;
}

.number-input-control:hover {
  background-color: var(--surface-secondary);
  transform: scale(1.05);
}

.number-input-control:active {
  transform: scale(0.95);
}

/* Value change animation */
.number-input-value {
  transition: all 0.2s ease-out;
}

.number-input-value.changed {
  animation: value-change 0.3s ease-out;
}

@keyframes value-change {
  0% { transform: scale(1); color: inherit; }
  50% { transform: scale(1.1); color: var(--accent-operational); }
  100% { transform: scale(1); color: inherit; }
}
```

### 4. Status and Notification Animations

#### Status Indicator Changes
```css
.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  transition: all 0.3s ease-out;
  position: relative;
}

.status-indicator::before {
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

.status-indicator.active::before {
  opacity: 0.3;
  animation: status-pulse 2s ease-in-out infinite;
}

.status-indicator.normal {
  background-color: var(--status-normal);
}

.status-indicator.normal::before {
  background-color: var(--status-normal);
}

.status-indicator.warning {
  background-color: var(--status-warning);
}

.status-indicator.warning::before {
  background-color: var(--status-warning);
}

@keyframes status-pulse {
  0%, 100% { transform: scale(1); opacity: 0.3; }
  50% { transform: scale(1.2); opacity: 0.1; }
}
```

#### Notification Slides
```css
.notification-toast {
  transform: translateY(-100%);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.notification-toast.show {
  transform: translateY(0);
  opacity: 1;
}

.notification-toast.hiding {
  transform: translateY(-100%);
  opacity: 0;
}
```

### 5. Data Visualization Animations

#### Chart Animations
```css
.chart-bar {
  transform-origin: bottom;
  animation: bar-grow 0.6s ease-out forwards;
}

@keyframes bar-grow {
  from {
    transform: scaleY(0);
  }
  to {
    transform: scaleY(1);
  }
}

/* Staggered animations for multiple elements */
.chart-bar:nth-child(1) { animation-delay: 0.1s; }
.chart-bar:nth-child(2) { animation-delay: 0.2s; }
.chart-bar:nth-child(3) { animation-delay: 0.3s; }
.chart-bar:nth-child(4) { animation-delay: 0.4s; }
.chart-bar:nth-child(5) { animation-delay: 0.5s; }
```

#### Data Value Changes
```css
.data-value {
  transition: all 0.2s ease-out;
}

.data-value.updating {
  animation: data-update 0.4s ease-out;
}

@keyframes data-update {
  0% {
    transform: scale(1);
    color: inherit;
  }
  50% {
    transform: scale(1.05);
    color: var(--accent-operational);
  }
  100% {
    transform: scale(1);
    color: inherit;
  }
}
```

## Performance Optimization

### CSS Performance Best Practices

#### Efficient Animation Properties
```css
/* Use these properties for better performance */
.performant-animation {
  /* GPU-accelerated properties */
  transform: translateX(100px);
  opacity: 0.5;
  filter: blur(5px);
}

/* Avoid these properties for frequent animations */
.non-performant-animation {
  /* These trigger layout/reflow */
  width: 200px;
  height: 100px;
  left: 50px;
  top: 25px;
}
```

#### Hardware Acceleration
```css
.gpu-accelerated {
  /* Force GPU layer creation */
  transform: translateZ(0);
  will-change: transform;
  backface-visibility: hidden;
}
```

### JavaScript Performance

#### Animation Frame Optimization
```javascript
class PerformanceAnimator {
  constructor() {
    this.animations = new Map();
    this.rafId = null;
  }

  addAnimation(element, keyframes, options) {
    const animation = element.animate(keyframes, {
      ...options,
      // Use efficient timing
      easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
      // Remove when complete
      fill: 'forwards'
    });

    this.animations.set(element, animation);

    animation.addEventListener('finish', () => {
      this.animations.delete(element);
    });

    return animation;
  }

  cancelAll() {
    this.animations.forEach(animation => animation.cancel());
    this.animations.clear();
  }
}
```

## Accessibility Considerations

### Motion Preferences
```css
/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Enhanced animations for users who prefer motion */
@media (prefers-reduced-motion: no-preference) {
  .enhanced-motion {
    animation-duration: 0.6s;
    animation-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }
}
```

### Accessibility Enhancements
```css
/* Focus indicators with animation */
.focus-enhanced:focus {
  outline: 2px solid var(--accent-operational);
  outline-offset: 2px;
  animation: focus-ring 0.3s ease-out;
}

@keyframes focus-ring {
  from {
    outline-width: 1px;
    outline-offset: 0px;
  }
  to {
    outline-width: 2px;
    outline-offset: 2px;
  }
}
```

## Implementation Guidelines

### Animation Timing Standards

#### Manufacturing Environment Timing
- **Micro-interactions**: 100-200ms (fast, responsive)
- **Status Changes**: 200-300ms (noticeable but not slow)
- **Page Transitions**: 300-400ms (context switching)
- **Data Loading**: 200-500ms (perceived performance)
- **Major State Changes**: 400-600ms (significant transitions)

#### Easing Functions
```css
:root {
  /* Industrial timing functions */
  --ease-out-quick: cubic-bezier(0.4, 0, 1, 1);
  --ease-out-smooth: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-in-quick: cubic-bezier(0, 0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

### Testing and Validation

#### Performance Testing
```javascript
// Animation performance monitoring
const measureAnimationPerformance = (element) => {
  const startTime = performance.now();

  element.addEventListener('animationend', () => {
    const endTime = performance.now();
    const duration = endTime - startTime;

    console.log(`Animation duration: ${duration}ms`);

    // Flag if animation is too slow for production
    if (duration > 1000) {
      console.warn('Animation exceeds recommended duration');
    }
  });
};
```

## Common Mistakes to Avoid

### Performance Issues
- ❌ Animating non-transform properties
- ❌ Excessive animation duration
- ❌ Simultaneous complex animations
- ❌ Not respecting reduced motion preferences

### Usability Problems
- ❌ Distracting animations during critical tasks
- ❌ Inconsistent animation patterns
- ❌ Unclear animation purpose or meaning
- ❌ Animations that hide important information

### Accessibility Failures
- ❌ Ignoring motion preference settings
- ❌ Poor contrast in animated elements
- ❌ Lack of focus indicators
- ❌ Animation-induced motion sickness

This micro-interaction framework provides the foundation for creating responsive, professional interfaces that enhance usability without compromising the serious nature of manufacturing applications.