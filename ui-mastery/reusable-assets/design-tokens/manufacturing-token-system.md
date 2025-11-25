# Manufacturing Design Token System

A comprehensive design token system specifically engineered for manufacturing and industrial UI applications, providing consistency, accessibility, and context-appropriate styling.

## Token Architecture

### Token Categories
1. **Global Tokens**: Base values (raw numbers, colors)
2. **Semantic Tokens**: Contextual meanings (status, actions)
3. **Component Tokens**: Component-specific values
4. **Theme Tokens**: Manufacturing-specific themes

### Token Naming Convention
```
{category}-{subcategory}-{property}-{modifier}

Examples:
- color-primary-500
- spacing-control-medium
- typography-heading-large
- status-error-background
```

## Global Base Tokens

### Color System
```css
/* tokens/global/colors.css */
:root {
  /* Primary Color Palette */
  --color-blue-50: #eff6ff;
  --color-blue-100: #dbeafe;
  --color-blue-200: #bfdbfe;
  --color-blue-300: #93c5fd;
  --color-blue-400: #60a5fa;
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  --color-blue-700: #1d4ed8;
  --color-blue-800: #1e40af;
  --color-blue-900: #1e3a8a;
  --color-blue-950: #172554;

  /* Industrial Gray Scale */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  --color-gray-950: #030712;

  /* Safety Colors (ISO 3864 Compliant) */
  --color-safety-red-50: #fef2f2;
  --color-safety-red-100: #fee2e2;
  --color-safety-red-500: #ef4444;
  --color-safety-red-600: #dc2626;
  --color-safety-red-700: #b91c1c;
  --color-safety-red-800: #991b1b;
  --color-safety-red-900: #7f1d1d;

  --color-safety-orange-50: #fff7ed;
  --color-safety-orange-100: #ffedd5;
  --color-safety-orange-500: #f97316;
  --color-safety-orange-600: #ea580c;
  --color-safety-orange-700: #c2410c;
  --color-safety-orange-800: #9a3412;
  --color-safety-orange-900: #7c2d12;

  --color-safety-amber-50: #fffbeb;
  --color-safety-amber-100: #fef3c7;
  --color-safety-amber-500: #f59e0b;
  --color-safety-amber-600: #d97706;
  --color-safety-amber-700: #b45309;
  --color-safety-amber-800: #92400e;
  --color-safety-amber-900: #78350f;

  --color-safety-green-50: #f0fdf4;
  --color-safety-green-100: #dcfce7;
  --color-safety-green-500: #22c55e;
  --color-safety-green-600: #16a34a;
  --color-safety-green-700: #15803d;
  --color-safety-green-800: #166534;
  --color-safety-green-900: #14532d;

  /* Semantic Base Colors */
  --color-white: #ffffff;
  --color-black: #000000;
  --color-transparent: transparent;
}
```

### Typography Scale
```css
/* tokens/global/typography.css */
:root {
  /* Font Families */
  --font-family-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-family-serif: 'Source Serif Pro', Georgia, serif;
  --font-family-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;
  --font-family-display: 'Space Grotesk', system-ui, sans-serif;

  /* Font Sizes - Responsive Type Scale */
  --font-size-xs: 0.75rem;     /* 12px */
  --font-size-sm: 0.875rem;    /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg: 1.125rem;    /* 18px */
  --font-size-xl: 1.25rem;     /* 20px */
  --font-size-2xl: 1.5rem;     /* 24px */
  --font-size-3xl: 1.875rem;   /* 30px */
  --font-size-4xl: 2.25rem;    /* 36px */
  --font-size-5xl: 3rem;       /* 48px */
  --font-size-6xl: 3.75rem;    /* 60px */

  /* Font Weights */
  --font-weight-thin: 100;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;
  --font-weight-black: 900;

  /* Line Heights */
  --line-height-none: 1;
  --line-height-tight: 1.25;
  --line-height-snug: 1.375;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.625;
  --line-height-loose: 2;

  /* Letter Spacing */
  --letter-spacing-tighter: -0.05em;
  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: 0em;
  --letter-spacing-wide: 0.025em;
  --letter-spacing-wider: 0.05em;
  --letter-spacing-widest: 0.1em;
}
```

### Spatial System
```css
/* tokens/global/spacing.css */
:root {
  /* Base spacing unit (4px = 0.25rem) */
  --space-unit: 0.25rem;

  /* Spacing Scale */
  --space-0: 0;
  --space-1: calc(var(--space-unit) * 1);   /* 4px */
  --space-2: calc(var(--space-unit) * 2);   /* 8px */
  --space-3: calc(var(--space-unit) * 3);   /* 12px */
  --space-4: calc(var(--space-unit) * 4);   /* 16px */
  --space-5: calc(var(--space-unit) * 5);   /* 20px */
  --space-6: calc(var(--space-unit) * 6);   /* 24px */
  --space-8: calc(var(--space-unit) * 8);   /* 32px */
  --space-10: calc(var(--space-unit) * 10); /* 40px */
  --space-12: calc(var(--space-unit) * 12); /* 48px */
  --space-16: calc(var(--space-unit) * 16); /* 64px */
  --space-20: calc(var(--space-unit) * 20); /* 80px */
  --space-24: calc(var(--space-unit) * 24); /* 96px */
  --space-32: calc(var(--space-unit) * 32); /* 128px */

  /* Manufacturing-specific spacing */
  --space-control-min: calc(var(--space-unit) * 11); /* 44px - minimum touch target */
  --space-panel-gap: var(--space-4);
  --space-section-gap: var(--space-6);
  --space-component-gap: var(--space-3);
}
```

### Easing and Animation
```css
/* tokens/global/animation.css */
:root {
  /* Easing Functions */
  --ease-linear: linear;
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-industrial: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-emergency: cubic-bezier(0.68, -0.55, 0.265, 1.55);

  /* Animation Durations */
  --duration-instant: 0ms;
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 750ms;

  /* Manufacturing-specific timings */
  --duration-control-feedback: var(--duration-fast);
  --duration-status-change: var(--duration-normal);
  --duration-warning-pulse: 1000ms;
  --duration-emergency-flash: 500ms;
}
```

## Semantic Tokens

### Status System
```css
/* tokens/semantic/status.css */
:root {
  /* Operational Status */
  --status-running: var(--color-safety-green-600);
  --status-running-background: var(--color-safety-green-50);
  --status-running-border: var(--color-safety-green-200);

  --status-stopped: var(--color-gray-600);
  --status-stopped-background: var(--color-gray-100);
  --status-stopped-border: var(--color-gray-300);

  --status-warning: var(--color-safety-amber-600);
  --status-warning-background: var(--color-safety-amber-50);
  --status-warning-border: var(--color-safety-amber-200);

  --status-error: var(--color-safety-red-600);
  --status-error-background: var(--color-safety-red-50);
  --status-error-border: var(--color-safety-red-200);

  --status-maintenance: var(--color-blue-600);
  --status-maintenance-background: var(--color-blue-50);
  --status-maintenance-border: var(--color-blue-200);

  --status-unknown: var(--color-gray-500);
  --status-unknown-background: var(--color-gray-100);
  --status-unknown-border: var(--color-gray-300);
}
```

### Interactive Elements
```css
/* tokens/semantic/interactive.css */
:root {
  /* Primary Actions */
  --interactive-primary: var(--color-blue-600);
  --interactive-primary-hover: var(--color-blue-700);
  --interactive-primary-active: var(--color-blue-800);
  --interactive-primary-disabled: var(--color-gray-400);

  /* Secondary Actions */
  --interactive-secondary: var(--color-gray-600);
  --interactive-secondary-hover: var(--color-gray-700);
  --interactive-secondary-active: var(--color-gray-800);
  --interactive-secondary-disabled: var(--color-gray-400);

  /* Critical Actions */
  --interactive-danger: var(--color-safety-red-600);
  --interactive-danger-hover: var(--color-safety-red-700);
  --interactive-danger-active: var(--color-safety-red-800);
  --interactive-danger-disabled: var(--color-gray-400);

  /* Focus States */
  --interactive-focus-ring: var(--color-blue-500);
  --interactive-focus-offset: 2px;
  --interactive-focus-width: 2px;
}
```

### Data Visualization
```css
/* tokens/semantic/data-viz.css */
:root {
  /* Chart Colors - Manufacturing Optimized */
  --data-primary: var(--color-blue-600);
  --data-secondary: var(--color-gray-600);
  --data-accent: var(--color-safety-green-600);
  --data-warning: var(--color-safety-amber-600);
  --data-danger: var(--color-safety-red-600);

  /* Data Visualization Context */
  --data-grid: var(--color-gray-200);
  --data-axis: var(--color-gray-400);
  --data-label: var(--color-gray-700);
  --data-background: var(--color-white);
  --data-legend-text: var(--color-gray-600);
}
```

## Component Tokens

### Button System
```css
/* tokens/components/buttons.css */
:root {
  /* Button Sizes */
  --button-height-small: var(--space-8);          /* 32px */
  --button-height-medium: var(--space-10);        /* 40px */
  --button-height-large: var(--space-12);         /* 48px */
  --button-height-emergency: var(--space-30);     /* 120px */

  /* Button Padding */
  --button-padding-x-small: var(--space-3);       /* 12px */
  --button-padding-x-medium: var(--space-4);      /* 16px */
  --button-padding-x-large: var(--space-6);       /* 24px */

  /* Button Borders */
  --button-border-width: 2px;
  --button-border-radius: 6px;
  --button-border-radius-emergency: 50%;

  /* Button Typography */
  --button-font-size: var(--font-size-sm);
  --button-font-weight: var(--font-weight-semibold);
  --button-letter-spacing: 0.025em;
  --button-text-transform: uppercase;
}
```

### Form Controls
```css
/* tokens/components/forms.css */
:root {
  /* Input Fields */
  --input-height: var(--space-control-min);       /* 44px - glove compatible */
  --input-padding-x: var(--space-3);              /* 12px */
  --input-border-width: 2px;
  --input-border-radius: 4px;
  --input-font-size: var(--font-size-base);
  --input-background: var(--color-white);

  /* Input States */
  --input-border-default: var(--color-gray-300);
  --input-border-focus: var(--color-blue-500);
  --input-border-error: var(--color-safety-red-500);
  --input-border-success: var(--color-safety-green-500);

  /* Labels */
  --label-font-size: var(--font-size-sm);
  --label-font-weight: var(--font-weight-medium);
  --label-color: var(--color-gray-700);
  --label-margin-bottom: var(--space-2);
}
```

### Status Indicators
```css
/* tokens/components/status.css */
:root {
  /* Status Indicators */
  --status-indicator-size: var(--space-3);        /* 12px */
  --status-indicator-size-large: var(--space-4);  /* 16px */
  --status-indicator-border-radius: 50%;

  /* Status Animations */
  --status-pulse-duration: var(--duration-warning-pulse);
  --status-pulse-opacity: 0.3;
  --status-pulse-scale: 1.2;

  /* Alert Banners */
  --alert-padding: var(--space-4);
  --alert-border-radius: 6px;
  --alert-border-width: 4px;
  --alert-font-size: var(--font-size-sm);
}
```

## Theme Tokens

### Manufacturing Themes
```css
/* tokens/themes/factory-floor.css`
:root {
  /* Factory Floor Theme - Bright lighting conditions */
  --theme-primary: var(--color-gray-800);
  --theme-secondary: var(--color-gray-600);
  --theme-accent: var(--color-blue-600);
  --theme-surface: var(--color-white);
  --theme-surface-secondary: var(--color-gray-50);
  --theme-border: var(--color-gray-200);
  --theme-text-primary: var(--color-gray-900);
  --theme-text-secondary: var(--color-gray-700);
  --theme-text-tertiary: var(--color-gray-500);
}

/* tokens/themes/control-room.css */
:root {
  /* Control Room Theme - Lower lighting conditions */
  --theme-primary: var(--color-gray-100);
  --theme-secondary: var(--color-gray-300);
  --theme-accent: var(--color-blue-400);
  --theme-surface: var(--color-gray-900);
  --theme-surface-secondary: var(--color-gray-800);
  --theme-border: var(--color-gray-700);
  --theme-text-primary: var(--color-white);
  --theme-text-secondary: var(--color-gray-300);
  --theme-text-tertiary: var(--color-gray-500);
}

/* tokens/themes/outdoor-industrial.css */
:root {
  /* Outdoor Industrial Theme - High contrast, sunlight readable */
  --theme-primary: var(--color-black);
  --theme-secondary: var(--color-gray-800);
  --theme-accent: var(--color-blue-700);
  --theme-surface: var(--color-white);
  --theme-surface-secondary: var(--color-gray-100);
  --theme-border: var(--color-gray-400);
  --theme-text-primary: var(--color-black);
  --theme-text-secondary: var(--color-gray-800);
  --theme-text-tertiary: var(--color-gray-600);
}
```

## Token Usage Guidelines

### Implementation Rules

#### 1. Use Semantic Tokens for Components
```css
/* Good - semantic */
.my-button {
  background-color: var(--interactive-primary);
  color: var(--color-white);
}

/* Avoid - direct color values */
.my-button {
  background-color: #2563eb; /* Don't do this */
}
```

#### 2. Scale Responsively
```css
.responsive-text {
  font-size: var(--font-size-base);
}

@media (min-width: 768px) {
  .responsive-text {
    font-size: var(--font-size-lg);
  }
}
```

#### 3. Respect Manufacturing Context
```css
/* Control interface components */
.control-panel {
  background: var(--theme-surface);
  border: 1px solid var(--theme-border);
  padding: var(--space-panel-gap);
}

/* Safety-critical elements */
.emergency-control {
  background: var(--status-error);
  animation: emergency-pulse var(--duration-emergency-flash) infinite;
}
```

### Token Maintenance

#### Version Control
- **Major Changes**: Breaking changes requiring component updates
- **Minor Changes**: New tokens or non-breaking modifications
- **Patch Changes**: Documentation updates or minor corrections

#### Update Process
1. **Design Review**: Validate changes against design system
2. **Impact Analysis**: Identify affected components
3. **Implementation**: Update tokens and components
4. **Testing**: Verify visual and functional correctness
5. **Documentation**: Update all references and examples

This comprehensive design token system provides the foundation for building consistent, accessible, and context-appropriate manufacturing interfaces while maintaining scalability and maintainability.